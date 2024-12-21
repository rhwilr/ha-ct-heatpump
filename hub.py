from __future__ import annotations

import asyncio

from websockets.asyncio.client import connect
import xmltodict

from homeassistant.core import HomeAssistant


class Hub:
    """CTA Heatpump integration"""

    manufacturer = "Demonstration Corp"

    def __init__(self, hass: HomeAssistant, host: str, password: str) -> None:
        """Init dummy hub."""
        self.host = host
        self.login = password

        self._hass = hass
        self._name = host
        self._id = host.lower()

        self.device = Heatpump(self._id, self._name, self)

        self.online = True
        self._notifier_task = False

    @property
    def hub_id(self) -> str:
        """ID for dummy hub."""
        return self._id

    async def test_connection(self) -> bool:
        """Test connectivity to the device is OK."""
        await self.device.test_connection()
        return True


class Heatpump:
    subprotocols = ["Lux_WS"]

    def __init__(self, deviceid: str, name: str, hub: Hub) -> None:
        self._id = deviceid
        self.hub = hub
        self.name = name

        self.values = list[lux_value]()

        self._loop = asyncio.get_running_loop()
        self._loop.create_task(self.update_ws())

    async def test_connection(self):
        return True

    async def update_ws(self):
        while True:
            await asyncio.sleep(3)

            async with connect(
                f"ws://{self.hub.host}:8214", subprotocols=self.subprotocols
            ) as websocket:
                await websocket.send(f"LOGIN;{self.hub.login}")

                # Navigation
                await self.on_message(websocket, await websocket.recv())

                # Get Content
                await self.on_message(websocket, await websocket.recv())

                # Close connection
                await websocket.close()

    def _get_info_id(self, data: dict) -> str:
        return data["Navigation"]["item"]["@id"]

    async def on_message(self, wsapp, message):
        data = xmltodict.parse(message)

        if "Navigation" in data:
            info_id = self._get_info_id(data)
            if info_id is not None:
                await wsapp.send(f"GET;{info_id}")
                return

        elif "Content" in data:
            self.values.clear()

            for cat_data in data["Content"]["item"]:
                cat_id = cat_data["@id"]
                cat = cat_data["name"][0]
                items = (
                    cat_data["item"]
                    if isinstance(cat_data["item"], list)
                    else [cat_data["item"]]
                )
                for value in items:
                    try:
                        self.values.extend(self._create_value_item(cat_id, cat, value))
                    except Exception as err:
                        print(f"Error: {err} {items}")
            return

    def _create_value_item(self, cat_id, cat, value):
        if "item" in value:
            cat = value["name"][0]
            return [lux_value(cat_id, cat, value_i) for value_i in value["item"]]

        return [lux_value(cat_id, cat, value)]

    def get_lux_value(self, category, name):
        return next(
            (
                value
                for value in self.values
                if value.category == category and value.name == name
            ),
            None,
        )

    @property
    def device_id(self) -> str:
        """Return ID for roller."""
        return self._id


class lux_value:
    value = None
    unit = None

    def __init__(self, cat_id: str, cat: str, data: dict):
        def is_float(num) -> bool:
            try:
                return not (float(num)).is_integer()
            except:
                return False

        self.cat_id = cat_id
        self.category = cat
        self.id = data["@id"]
        self.name = data["name"]
        self.value = str(data["value"])
        self.unit = None

        if self.value == "Ein":
            self.value = True
        elif self.value == "Aus":
            self.value = False
        elif self.value.endswith("°C"):
            self.value = float(self.value[:-2])
            self.unit = "°C"
        elif self.value.endswith("K"):
            self.value = float(self.value[:-1])
            self.unit = "K"
        elif self.value.endswith("bar"):
            self.value = float(self.value[:-3])
            self.unit = "bar"
        elif self.value.endswith("l/h"):
            self.value = float(self.value[:-3]) / 60
            self.unit = "l/h"
        elif self.value.endswith("V"):
            self.value = float(self.value[:-1])
            self.unit = "V"
        elif self.value.endswith("%"):
            self.value = float(self.value[:-1])
            self.unit = "%"
        elif self.value.endswith("RPM"):
            self.value = float(self.value[:-3])
            self.unit = "RPM"
        elif self.value.endswith("kW"):
            self.value = float(self.value[:-2])
            self.unit = "kW"
        elif self.value.endswith("kWh"):
            self.value = float(self.value[:-3])
            self.unit = "kWh"
        elif self.value.endswith("h"):
            self.value = float(self.value[:-1])
            self.unit = "h"
        elif (
            " " in self.value
            and " (" not in self.value
            and not self.value.endswith(")")
        ):
            v = self.value.split(" ")
            if is_float(v):
                self.value = float(v[0])
                self.unit = v[1]

    def __repr__(self):
        return f"{self.category}.{self.name} ({self.id}): {self.value} {self.unit}"

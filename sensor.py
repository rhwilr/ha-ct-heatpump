"""Platform for sensor integration."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HubConfigEntry
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config: HubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    hub = config.runtime_data

    async_add_entities(
        [
            TemeraturSensor(hub.device, "Flow Temperature", "Temperaturen", "Vorlauf"),
            TemeraturSensor(
                hub.device, "Return Temperature", "Temperaturen", "Rücklauf"
            ),
            TemeraturSensor(
                hub.device, "Return Target Temperature", "Temperaturen", "Rückl.-Soll"
            ),
            TemeraturSensor(
                hub.device,
                "Outside Temperature",
                "Temperaturen",
                "Außentemperatur",
            ),
            TemeraturSensor(
                hub.device, "Hot Water (Actual)", "Temperaturen", "Warmwasser-Ist"
            ),
            TemeraturSensor(
                hub.device, "Hot Water (Target)", "Temperaturen", "Warmwasser-Soll"
            ),
            FlowRateSensor(hub.device, "Flow Rate", "Eingänge", "Durchfluss"),
            StatusSensor(
                hub.device, "Operating Condition", "Anlagenstatus", "Betriebszustand"
            ),
            PowerSensor(
                hub.device, "Performance (Actual)", "Anlagenstatus", "Leistung Ist"
            ),
            PercentageSensor(
                hub.device, "Defrost Requirement", "Anlagenstatus", "Abtaubedarf"
            ),
            EnergySensor(
                hub.device, "Heating Energy Quantity", "Wärmemenge", "Heizung"
            ),
            EnergySensor(
                hub.device, "Hot Water Energy Quantity", "Wärmemenge", "Warmwasser"
            ),
            EnergySensor(hub.device, "Total Energy Quantity", "Wärmemenge", "Gesamt"),
            EnergySensor(
                hub.device, "Energy Used for Heating", "Eingesetzte Energie", "Heizung"
            ),
            EnergySensor(
                hub.device,
                "Energy Used for Hot Water",
                "Eingesetzte Energie",
                "Warmwasser",
            ),
            EnergySensor(
                hub.device, "Total Energy Used", "Eingesetzte Energie", "Gesamt"
            ),
        ]
    )


class SensorBase(SensorEntity):
    """Base representation of a Hello World Sensor."""

    should_poll = True

    def __init__(self, device, name, lux_cat, lux_id) -> None:
        """Initialize the sensor."""
        self._device = device
        self._name = name
        self._lux_cat = lux_cat
        self._lux_id = lux_id
        self._state = None

        self._attr_unique_id = f"cta_heatpump-{self._name}"
        self._attr_name = f"CTA Heatpump - {self._name}"

        self.update()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._device.device_id)}}

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"CTA Heatpump - {self._name}"

    def update(self) -> None:
        lux_value = self._device.get_lux_value(self._lux_cat, self._lux_id)

        if lux_value is not None:
            self._state = lux_value.value


class TemeraturSensor(SensorBase):
    def __init__(self, device, name, lux_cat, lux_id):
        """Initialize the sensor."""
        super().__init__(device, name, lux_cat, lux_id)

        self.device_class = SensorDeviceClass.TEMPERATURE
        self.state_class = SensorStateClass.MEASUREMENT

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @property
    def icon(self) -> str:
        return "mdi:thermometer"


class FlowRateSensor(SensorBase):
    def __init__(self, device, name, lux_cat, lux_id):
        """Initialize the sensor."""
        super().__init__(device, name, lux_cat, lux_id)

        self.device_class = SensorDeviceClass.VOLUME_FLOW_RATE
        self.state_class = SensorStateClass.MEASUREMENT

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfVolumeFlowRate.LITERS_PER_MINUTE

    @property
    def icon(self) -> str:
        return "mdi:water"


class StatusSensor(SensorBase):
    def __init__(self, device, name, lux_cat, lux_id):
        """Initialize the sensor."""
        super().__init__(device, name, lux_cat, lux_id)

        self.state_class = SensorStateClass.MEASUREMENT

    @property
    def icon(self) -> str:
        return "mdi:format-list-bulleted"


class PowerSensor(SensorBase):
    def __init__(self, device, name, lux_cat, lux_id):
        """Initialize the sensor."""
        super().__init__(device, name, lux_cat, lux_id)

        self.device_class = SensorDeviceClass.POWER
        self.state_class = SensorStateClass.MEASUREMENT

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfPower.KILO_WATT

    @property
    def icon(self) -> str:
        return "mdi:heat-pump"


class PercentageSensor(SensorBase):
    def __init__(self, device, name, lux_cat, lux_id):
        """Initialize the sensor."""
        super().__init__(device, name, lux_cat, lux_id)

        self.state_class = SensorStateClass.MEASUREMENT

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def icon(self) -> str:
        return "mdi:snowflake-melt"


class EnergySensor(SensorBase):
    def __init__(self, device, name, lux_cat, lux_id):
        """Initialize the sensor."""
        super().__init__(device, name, lux_cat, lux_id)

        self.device_class = SensorDeviceClass.ENERGY
        self.state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def icon(self) -> str:
        return "mdi:lightning-bolt"

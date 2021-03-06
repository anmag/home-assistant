"""
This platform provides binary sensors for key RainMachine data.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.rainmachine/
"""
import logging

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.rainmachine import (
    BINARY_SENSORS, DATA_RAINMACHINE, SENSOR_UPDATE_TOPIC, TYPE_FREEZE,
    TYPE_FREEZE_PROTECTION, TYPE_HOT_DAYS, TYPE_HOURLY, TYPE_MONTH,
    TYPE_RAINDELAY, TYPE_RAINSENSOR, TYPE_WEEKDAY, RainMachineEntity)
from homeassistant.const import CONF_MONITORED_CONDITIONS
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

DEPENDENCIES = ['rainmachine']

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
        hass, config, async_add_entities, discovery_info=None):
    """Set up the RainMachine Switch platform."""
    if discovery_info is None:
        return

    rainmachine = hass.data[DATA_RAINMACHINE]

    binary_sensors = []
    for sensor_type in discovery_info[CONF_MONITORED_CONDITIONS]:
        name, icon = BINARY_SENSORS[sensor_type]
        binary_sensors.append(
            RainMachineBinarySensor(rainmachine, sensor_type, name, icon))

    async_add_entities(binary_sensors, True)


class RainMachineBinarySensor(RainMachineEntity, BinarySensorDevice):
    """A sensor implementation for raincloud device."""

    def __init__(self, rainmachine, sensor_type, name, icon):
        """Initialize the sensor."""
        super().__init__(rainmachine)

        self._icon = icon
        self._name = name
        self._sensor_type = sensor_type
        self._state = None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._icon

    @property
    def is_on(self):
        """Return the status of the sensor."""
        return self._state

    @property
    def should_poll(self):
        """Disable polling."""
        return False

    @property
    def unique_id(self) -> str:
        """Return a unique, HASS-friendly identifier for this entity."""
        return '{0}_{1}'.format(
            self.rainmachine.device_mac.replace(':', ''), self._sensor_type)

    @callback
    def _update_data(self):
        """Update the state."""
        self.async_schedule_update_ha_state(True)

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(
            self.hass, SENSOR_UPDATE_TOPIC, self._update_data)

    async def async_update(self):
        """Update the state."""
        if self._sensor_type == TYPE_FREEZE:
            self._state = self.rainmachine.restrictions['current']['freeze']
        elif self._sensor_type == TYPE_FREEZE_PROTECTION:
            self._state = self.rainmachine.restrictions['global'][
                'freezeProtectEnabled']
        elif self._sensor_type == TYPE_HOT_DAYS:
            self._state = self.rainmachine.restrictions['global'][
                'hotDaysExtraWatering']
        elif self._sensor_type == TYPE_HOURLY:
            self._state = self.rainmachine.restrictions['current']['hourly']
        elif self._sensor_type == TYPE_MONTH:
            self._state = self.rainmachine.restrictions['current']['month']
        elif self._sensor_type == TYPE_RAINDELAY:
            self._state = self.rainmachine.restrictions['current']['rainDelay']
        elif self._sensor_type == TYPE_RAINSENSOR:
            self._state = self.rainmachine.restrictions['current'][
                'rainSensor']
        elif self._sensor_type == TYPE_WEEKDAY:
            self._state = self.rainmachine.restrictions['current']['weekDay']

import logging
from datetime import datetime, timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from . import DOMAIN, garbage_types
from .utils import (check_settings, find_id, find_id_from_lat_lon,
                    get_tommeplan_page, parse_tomme_kalender)

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional("address", default=""): cv.string,
        vol.Optional("street_id", default=""): cv.string,
        vol.Optional("garbage_types", default=garbage_types): list,
    }
)


MIN_TIME_BETWEEN_UPDATES = timedelta(weeks=4)


async def dry_setup(hass, config_entry, async_add_devices):
    config = config_entry
    street_id = config.get("street_id")
    address = config.get("address")

    check_settings(config, hass)
    data = AvfallSorData(
        address,
        street_id,
        hass.config.latitude,
        hass.config.longitude,
        async_get_clientsession(hass),
    )

    await data.update()
    sensors = []
    for gb_type in config.get("garbage_types"):
        sensor = AvfallSor(data, gb_type)
        sensors.append(sensor)

    async_add_devices(sensors)


async def async_setup_platform(
    hass, config_entry, async_add_devices, discovery_info=None
):
    """Setup sensor platform for the ui"""
    await dry_setup(hass, config_entry, async_add_devices)
    return True


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform for the ui"""
    config = config_entry.data
    await dry_setup(hass, config, async_add_devices)
    return True


async def async_remove_entry(hass, config_entry):
    _LOGGER.info("async_remove_entry avfallsor")
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed sensor from the avfallsor integration")
    except ValueError:
        pass


class AvfallSorData:
    def __init__(self, address, street_id, lat, lon, client):
        self._address = address
        self._street_id = street_id
        self.client = client
        self._data = {}
        self._last_update = None
        self._lat = lat
        self._lon = lon
        self._friendly_name = None

    async def find_street_id(self):
        """Helper to get get the correct info with the least possible setup

        Find the info using different methods where the prios are:
        1. streetid
        2. address
        3. lat and lon set in ha config when this was setup.

        """
        # use
        # verify_that_we_can_find_id
        if not len(self._street_id):
            if self._address:
                result = await find_id(self._address, self.client)
                if result:
                    self._street_id = result
                    return
            if self._lat and self._lon and self._street_id is None:
                result = await find_id_from_lat_lon(self._lat, self._lon, self.client)
                if result:
                    self._street_id = result
                    return

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def _update(self):
        _LOGGER.debug("Fetching stuff for AvfallSorData")
        await self.find_street_id()
        if self._street_id:
            text = await get_tommeplan_page(self._street_id, self.client)
        else:
            return

        if text:
            self._data = parse_tomme_kalender(text)
            self._last_update = datetime.now()

    async def update(self):
        await self._update()
        return self._data


class AvfallSor(Entity):
    def __init__(self, data, garbage_type):
        self.data = data
        self._garbage_type = garbage_type

    @property
    def state(self):
        """Return the state of the sensor."""
        nxt = self.next_garbage_pickup
        if nxt is not None:
            delta = nxt.date() - datetime.today().date()
            return delta.days

    async def async_update(self):
        await self.data.update()

    @property
    def next_garbage_pickup(self):
        """Get the date of the next picked for that garbage type."""
        return self.data._data.get(self._garbage_type)

    @property
    def icon(self) -> str:
        """Shows the correct icon for container."""
        icons = {
            "paper": "mdi:note-text-outline",
            "bio": "mdi:compost",
            "mixed": "mdi:trash-can",
            "metal": "mdi:bottle-wine",
            "plastic": "mdi:recycle-variant"
        }
        return icons[self._garbage_type]

    @property
    def unique_id(self) -> str:
        """Return the name of the sensor."""
        return (
            f"avfallsor_{self._garbage_type}_{self.data._street_id.replace('-', '_')}"
        )

    @property
    def name(self) -> str:
        return self.unique_id

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            "next garbage pickup": self.next_garbage_pickup,
            ATTR_ATTRIBUTION: "avfallsør",
            "last update": self.data._last_update,
            "garbage_type": self._garbage_type
        }

    @property
    def device_info(self) -> dict:
        """I can't remember why this was needed :D"""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": DOMAIN,
        }

    @property
    def unit(self) -> int:
        """Unit"""
        return int

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement this sensor expresses itself in."""
        return "days"

    @property
    def friendly_name(self) -> str:
        return self._friendly_name

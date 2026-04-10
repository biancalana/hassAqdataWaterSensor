"""Sensor platform for AqData integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AqDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up AqData sensors from a config entry."""
    coordinator: AqDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        AqDataReadingSensor(coordinator, config_entry),
        AqDataConsumptionSensor(coordinator, config_entry),
    ])


class AqDataBaseSensor(CoordinatorEntity[AqDataCoordinator], SensorEntity):
    """Base sensor for AqData."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AqDataCoordinator,
        config_entry: ConfigType,
    ) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "AqData Hidrômetro",
            "manufacturer": "AqData",
        }


class AqDataReadingSensor(AqDataBaseSensor):
    """Sensor for the totalizer (absolute meter reading in m³)."""

    _attr_name = "Leitura"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_suggested_display_precision = 3

    @property
    def native_value(self) -> float | None:
        """Return the totalizer value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("totalizer")

    @property
    def extra_state_attributes(self) -> dict:
        """Return the reading date."""
        if self.coordinator.data is None:
            return {}
        return {"date": self.coordinator.data.get("date")}


class AqDataConsumptionSensor(AqDataBaseSensor):
    """Sensor for consumption since last reading (m³)."""

    _attr_name = "Consumo"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_suggested_display_precision = 3

    @property
    def native_value(self) -> float | None:
        """Return the consumption value."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("consumption")

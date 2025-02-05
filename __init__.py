"""The Notification Tap Events integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, Event
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, EVENT_NOTIFICATION_TAPPED

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Notification Tap Events from a config entry."""
    
    async def handle_mobile_app_notification_action(event: Event) -> None:
        """Handle mobile_app_notification_action events."""
        if event.data.get("action") == "tap":
            notification_data = event.data.get("data", {})
            
            hass.bus.async_fire(
                EVENT_NOTIFICATION_TAPPED,
                {
                    "device_id": event.data.get("device_id"),
                    "notification_id": notification_data.get("notification_id"),
                    "title": notification_data.get("title"),
                    "message": notification_data.get("message"),
                    "data": notification_data
                }
            )

    # Subscribe to mobile_app_notification_action events
    entry.async_on_unload(
        hass.bus.async_listen(
            "mobile_app_notification_action",
            handle_mobile_app_notification_action
        )
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
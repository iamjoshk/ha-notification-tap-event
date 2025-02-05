"""HA Notification Tap Event integration."""
import logging
import voluptuous as vol
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.const import ATTR_MESSAGE, ATTR_DATA
import homeassistant.helpers.config_validation as cv
from homeassistant.components import websocket_api

from .const import DOMAIN, EVENT_TYPE

_LOGGER = logging.getLogger(__name__)

SERVICE_NOTIFY = "notify"
ATTR_TARGET = "target"

NOTIFICATION_SCHEMA = vol.Schema({
    vol.Required(ATTR_MESSAGE): cv.string,
    vol.Optional(ATTR_TARGET): cv.string,
    vol.Optional(ATTR_DATA): dict
})

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the notification tap event platform."""

    @callback
    @websocket_api.websocket_command({
        "type": "mobile_app/notification_clicked",
        vol.Required("notification_id"): str,
        vol.Required("action"): str,
    })
    def handle_notification_click(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
        """Handle notification click events from mobile app."""
        _LOGGER.debug("Received notification click: %s", msg)

        # Fire our custom event
        hass.bus.async_fire(EVENT_TYPE, {
            "notification_id": msg["notification_id"],
            "action": msg["action"],
            "click_action": msg.get("click_action"),
            "data": msg.get("data", {})
        })

    # Register websocket command
    websocket_api.async_register_command(hass, handle_notification_click)
    _LOGGER.debug("Registered notification click handler")

    async def handle_notify(call: ServiceCall) -> None:
        """Handle the notification service call."""
        message = call.data.get(ATTR_MESSAGE)
        target = call.data.get(ATTR_TARGET)
        data = call.data.get(ATTR_DATA, {})

        # Add our event handling to the notification
        if "clickAction" in data:
            # Add a tag to track this notification
            notification_id = data.get("tag", f"notify_{hash(message)}")
            data["tag"] = notification_id
            
            # Add action that will fire our event
            data["actions"] = data.get("actions", []) + [{
                "action": "TAP_EVENT",
                "title": "Tap",
                "launch": True
            }]

        # Forward to mobile_app notification
        service_data = {
            "message": message,
            "data": data
        }
        if target:
            service_data["target"] = target

        await hass.services.async_call("notify", "mobile_app", service_data)

    # Register our notification service
    hass.services.register(DOMAIN, SERVICE_NOTIFY, handle_notify, schema=NOTIFICATION_SCHEMA)
    
    return True
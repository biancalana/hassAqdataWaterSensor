import json
import logging
import time

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

DISCOVERY_PREFIX = "homeassistant"
DEVICE_ID = "aqdata_water"


def _device_info():
    return {
        "identifiers": [DEVICE_ID],
        "name": "AqData Hidrômetro",
        "manufacturer": "AqData",
    }


def publish_readings(
    host: str,
    port: int,
    user: str,
    password: str,
    totalizer: float,
    consumption: float,
    retries: int = 3,
) -> bool:
    """Connect to MQTT broker, publish auto-discovery config and sensor values."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="aqdata_scraper")
    if user and password:
        client.username_pw_set(user, password)

    connected = False
    for attempt in range(1, retries + 1):
        try:
            client.connect(host, port, 60)
            client.loop_start()
            connected = True
            break
        except Exception as e:
            logger.warning("MQTT connect failed (attempt %d/%d): %s", attempt, retries, e)
            if attempt < retries:
                time.sleep(2 * attempt)

    if not connected:
        logger.error("Could not connect to MQTT broker after %d attempts", retries)
        return False

    try:
        # Auto-discovery: totalizer sensor
        client.publish(
            f"{DISCOVERY_PREFIX}/sensor/aqdata_water_reading/config",
            json.dumps({
                "unique_id": "aqdata_water_reading",
                "name": "Leitura Hidrômetro",
                "state_topic": f"{DISCOVERY_PREFIX}/sensor/aqdata_water_reading/state",
                "unit_of_measurement": "m³",
                "icon": "mdi:water-meter",
                "state_class": "total_increasing",
                "device_class": "water",
                "device": _device_info(),
            }),
            retain=True,
        )

        # Auto-discovery: consumption sensor
        client.publish(
            f"{DISCOVERY_PREFIX}/sensor/aqdata_water_consumption/config",
            json.dumps({
                "unique_id": "aqdata_water_consumption",
                "name": "Consumo Diário Água",
                "state_topic": f"{DISCOVERY_PREFIX}/sensor/aqdata_water_consumption/state",
                "unit_of_measurement": "m³",
                "icon": "mdi:water",
                "state_class": "measurement",
                "device_class": "water",
                "device": _device_info(),
            }),
            retain=True,
        )

        # State values
        client.publish(
            f"{DISCOVERY_PREFIX}/sensor/aqdata_water_reading/state",
            f"{totalizer:.3f}",
            retain=True,
        )
        client.publish(
            f"{DISCOVERY_PREFIX}/sensor/aqdata_water_consumption/state",
            f"{consumption:.3f}",
            retain=True,
        )

        # Wait for messages to be sent
        client.loop_stop()
        client.disconnect()

        logger.info("MQTT published: reading=%.3f m³, consumption=%.3f m³", totalizer, consumption)
        return True

    except Exception as e:
        logger.error("MQTT publish error: %s", e)
        client.loop_stop()
        client.disconnect()
        return False

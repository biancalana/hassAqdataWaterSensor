import json
import logging
from datetime import timezone

import websocket

logger = logging.getLogger(__name__)


def import_statistics(
    ha_url: str,
    ha_token: str,
    readings: list,
) -> bool:
    """Import historical readings via HA WebSocket statistics import API.

    Each reading must have .date, .totalizer, .consumption attributes.
    Timestamps are aligned to the top of the hour (HA requirement).
    Data appears in the HA Water/Energy dashboard as external statistics.
    """
    ws_url = ha_url.replace("http://", "ws://").replace("https://", "wss://")
    ws_url = f"{ws_url}/api/websocket"

    try:
        ws = websocket.create_connection(ws_url, timeout=30)
    except Exception as e:
        logger.error("WebSocket connection failed: %s", e)
        return False

    try:
        # Authenticate
        ws.recv()  # auth_required message
        ws.send(json.dumps({"type": "auth", "access_token": ha_token}))
        auth_result = json.loads(ws.recv())
        if auth_result.get("type") != "auth_ok":
            logger.error("HA auth failed: %s", auth_result.get("message", ""))
            return False

        logger.info("WebSocket authenticated")

        # Build stats arrays
        totalizer_stats = []
        consumption_stats = []
        first_totalizer = readings[0].totalizer

        for reading in readings:
            start = reading.date.replace(minute=0, second=0, microsecond=0)
            start_iso = start.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

            totalizer_stats.append({
                "start": start_iso,
                "state": reading.totalizer,
                "sum": round(reading.totalizer - first_totalizer, 6),
            })

            consumption_stats.append({
                "start": start_iso,
                "mean": reading.consumption,
                "min": reading.consumption,
                "max": reading.consumption,
            })

        # Import totalizer — external statistics
        ws.send(json.dumps({
            "id": 1,
            "type": "recorder/import_statistics",
            "metadata": {
                "statistic_id": "aqdata:water_total",
                "source": "aqdata",
                "name": "Leitura Hidrômetro",
                "has_sum": True,
                "mean_type": 0,
                "unit_of_measurement": "m³",
                "unit_class": "volume",
            },
            "stats": totalizer_stats,
        }))
        result = json.loads(ws.recv())
        if not result.get("success"):
            logger.error("Totalizer import failed: %s", result)
            return False

        logger.info("Imported %d totalizer statistics", len(totalizer_stats))

        # Import consumption — external statistics
        ws.send(json.dumps({
            "id": 2,
            "type": "recorder/import_statistics",
            "metadata": {
                "statistic_id": "aqdata:water_consumption",
                "source": "aqdata",
                "name": "Consumo Diário Água",
                "has_sum": False,
                "mean_type": 1,
                "unit_of_measurement": "m³",
                "unit_class": "volume",
            },
            "stats": consumption_stats,
        }))
        result = json.loads(ws.recv())
        if not result.get("success"):
            logger.error("Consumption import failed: %s", result)
            return False

        logger.info("Imported %d consumption statistics", len(consumption_stats))

        return True

    except Exception as e:
        logger.error("Statistics import error: %s", e)
        return False
    finally:
        ws.close()

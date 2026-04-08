#!/usr/bin/env python3
"""AqData water meter scraper — fetches readings and sends to Home Assistant via MQTT."""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

from aqdata.auth import login
from aqdata.config import load_config
from aqdata.mqtt import publish_readings
from aqdata.scraper import fetch_readings
from aqdata.state import get_last_date, load_state, save_state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    config = load_config()
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    # Login
    if not login(session, config.base_url, config.user, config.password):
        logger.error("Login failed, aborting")
        sys.exit(1)

    # Determine date range
    state = load_state()
    today = datetime.now()

    if config.since:
        start_date = config.since
    else:
        last_date = get_last_date(state)
        if last_date:
            start_date = last_date + timedelta(days=1)
        else:
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # Fetch readings
    readings = fetch_readings(session, config.base_url, config.medidor_id, start_date, today)
    if not readings:
        logger.info("No new readings found")
        sys.exit(0)

    # Use the latest reading
    latest = readings[-1]
    logger.info(
        "Latest reading: date=%s totalizer=%.3f m³ consumption=%.3f m³",
        latest.date.isoformat(), latest.totalizer, latest.consumption,
    )

    # Send to Home Assistant via MQTT
    if not config.dry_run:
        if not publish_readings(
            config.mqtt_host, config.mqtt_port,
            config.mqtt_user, config.mqtt_password,
            latest.totalizer, latest.consumption,
        ):
            logger.error("Failed to publish to MQTT")
            sys.exit(1)
    else:
        logger.info("Dry run — skipping MQTT publish")

    # Update state
    save_state(
        Path("state.json"),
        latest.date.strftime("%Y-%m-%d"),
        latest.totalizer,
        latest.consumption,
    )


if __name__ == "__main__":
    main()

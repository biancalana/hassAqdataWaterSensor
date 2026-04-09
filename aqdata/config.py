import argparse
import os
from datetime import datetime
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    base_url: str
    user: str
    password: str
    medidor_id: str
    mqtt_host: str
    mqtt_port: int
    mqtt_user: str
    mqtt_password: str
    ha_url: str
    ha_token: str
    since: datetime | None
    dry_run: bool


def parse_args():
    parser = argparse.ArgumentParser(description="AqData water meter scraper")
    parser.add_argument("--since", type=lambda s: datetime.strptime(s, "%Y-%m-%d"), help="Fetch readings since this date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending data to Home Assistant")
    return parser.parse_args()


def load_config() -> Config:
    load_dotenv()

    args = parse_args()

    required = ["AQDATA_USER", "AQDATA_PASSWORD", "MQTT_HOST"]
    if args.since:
        required += ["HA_URL", "HA_TOKEN"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise SystemExit(f"Missing required env vars: {', '.join(missing)}")

    return Config(
        base_url=os.getenv("AQDATA_BASE_URL", "https://sistema.aqdata.com.br"),
        user=os.getenv("AQDATA_USER"),
        password=os.getenv("AQDATA_PASSWORD"),
        medidor_id=os.getenv("AQDATA_MEDIDOR_ID", ""),
        mqtt_host=os.getenv("MQTT_HOST"),
        mqtt_port=int(os.getenv("MQTT_PORT", "1883")),
        mqtt_user=os.getenv("MQTT_USER", ""),
        mqtt_password=os.getenv("MQTT_PASSWORD", ""),
        ha_url=os.getenv("HA_URL", "").rstrip("/"),
        ha_token=os.getenv("HA_TOKEN", ""),
        since=args.since,
        dry_run=args.dry_run,
    )

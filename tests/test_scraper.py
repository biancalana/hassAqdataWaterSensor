"""Tests for AqData scraper parse logic.

Tests the pure parse functions extracted from the scraper,
without needing the full HA environment.
"""

from datetime import datetime
from bs4 import BeautifulSoup


# --- Extracted pure functions from scraper.py for testing ---
# (These mirror the logic in custom_components/aqdata/scraper.py)

def _parse_brazilian_number(text: str) -> float:
    if not text or text == "\xa0":
        return 0.0
    return float(text.replace(".", "").replace(",", "."))


def _parse_readings(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    readings: list[dict] = []
    for tr in soup.find_all("tr"):
        cells = tr.find_all("td")
        if len(cells) < 7:
            continue
        date_text = cells[4].get_text(strip=True)
        if not date_text or date_text == "\xa0":
            continue
        try:
            parsed_date = datetime.strptime(date_text, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            continue
        totalizer = _parse_brazilian_number(cells[5].get_text(strip=True))
        consumption = _parse_brazilian_number(cells[6].get_text(strip=True))
        readings.append({
            "date": parsed_date.isoformat(),
            "totalizer": totalizer,
            "consumption": consumption,
        })
    return readings


# --- Sample HTML (mimics diario_iot page) ---

SAMPLE_HTML = """
<table>
<tbody>
<tr>
<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
<td>08/04/2026 00:00:00</td>
<td>823,450</td>
<td>1,200</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
<td>09/04/2026 00:00:00</td>
<td>823,450</td>
<td>0,000</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
</tbody>
</table>
"""


# --- Tests ---

def test_parse_brazilian_number():
    assert _parse_brazilian_number("823,450") == 823.45
    assert _parse_brazilian_number("0,000") == 0.0
    assert _parse_brazilian_number("1.234,567") == 1234.567
    assert _parse_brazilian_number("\xa0") == 0.0
    assert _parse_brazilian_number("") == 0.0


def test_parse_readings_returns_correct_count():
    readings = _parse_readings(SAMPLE_HTML)
    assert len(readings) == 2


def test_parse_readings_latest_values():
    readings = _parse_readings(SAMPLE_HTML)
    # Server returns oldest first, so [-1] is latest (Apr 9)
    latest = readings[-1]
    assert latest["totalizer"] == 823.45
    assert latest["consumption"] == 0.0
    assert latest["date"] == "2026-04-09T00:00:00"


def test_parse_readings_earlier_values():
    readings = _parse_readings(SAMPLE_HTML)
    assert readings[0]["totalizer"] == 823.45
    assert readings[0]["consumption"] == 1.2


def test_parse_readings_empty_html():
    readings = _parse_readings("<html><body></body></html>")
    assert readings == []


if __name__ == "__main__":
    test_parse_brazilian_number()
    test_parse_readings_returns_correct_count()
    test_parse_readings_latest_values()
    test_parse_readings_earlier_values()
    test_parse_readings_empty_html()
    print("All tests passed!")

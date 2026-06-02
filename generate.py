import re
import requests
from datetime import datetime
from email.utils import format_datetime
from xml.sax.saxutils import escape

URL = "http://www.koeri.boun.edu.tr/scripts/lst8.asp"

response = requests.get(URL, timeout=20)
response.encoding = "iso-8859-9"
text = response.text

rows = []

for line in text.splitlines():
    line = line.strip()

    if re.match(r"^\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}:\d{2}", line):
        parts = line.split()

        if len(parts) < 9:
            continue

        date = parts[0]
        time = parts[1]
        lat = parts[2]
        lon = parts[3]
        depth = parts[4]
        mag = parts[6]
        location = " ".join(parts[8:])

        rows.append({
            "date": date,
            "time": time,
            "lat": lat,
            "lon": lon,
            "depth": depth,
            "mag": mag,
            "location": location,
        })

items = ""

for r in rows[:50]:
    title = f"M{r['mag']} - {r['location']}"
    desc = (
        f"Tarih: {r['date']} {r['time']} | "
        f"Derinlik: {r['depth']} km | "
        f"Konum: {r['lat']}, {r['lon']}"
    )

    guid = f"{r['date']}-{r['time']}-{r['lat']}-{r['lon']}-{r['mag']}"

    items += f"""
    <item>
      <title>{escape(title)}</title>
      <link>{URL}</link>
      <guid>{escape(guid)}</guid>
      <description>{escape(desc)}</description>
    </item>
"""

rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Kandilli Son Depremler</title>
  <link>{URL}</link>
  <description>Kandilli Rasathanesi son depremler RSS feed</description>
  <lastBuildDate>{format_datetime(datetime.now().astimezone())}</lastBuildDate>
  {items}
</channel>
</rss>
"""

with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(rss)

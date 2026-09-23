import requests
import json
from bs4 import BeautifulSoup

URL = "https://www.hcpcsdata.com/Codes/A"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
}

response = requests.get(URL, headers=headers, timeout=30)

print("Status code:", response.status_code)
print("Response length:", len(response.text))

soup = BeautifulSoup(response.text, "html.parser")

rows = soup.find_all("tr", class_="clickable-row")

print("Number of rows:", len(rows))

records = []

for row in rows:
    cells = row.find_all("td")

    if len(cells)>=2:
        code = cells[0].get_text(strip=True)
        description = cells[1].get_text(" ",strip=True)

        records.append({
            "hcpcs_code":code,
            "description":description
        })

print("Records extracted:",len(records))

with open("raw/hcpcs_a_codes.json","w", encoding="utf-8") as file:
    json.dump(records, file, indent=2, ensure_ascii=False)

print("Raw data saved to raw/hcpcs_a_codes.json")
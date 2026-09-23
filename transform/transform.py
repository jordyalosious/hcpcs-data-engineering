import json
import hashlib

INPUT_FILE = "raw/hcpcs_a_codes.json"

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    records = json.load(file)

transformed_records = []

for record in records:

    code = record["hcpcs_code"].strip()
    description = record["description"].strip()

    desc_hash = hashlib.md5(
        description.encode("utf-8")
    ).hexdigest()

    transformed_records.append({
        "hcpcs_code": code,
        "description": description,
        "desc_hash": desc_hash
    })

print("Records transformed:", len(transformed_records))
print("Total records:", len(transformed_records))

missing_codes = [
    record for record in transformed_records
    if not record["hcpcs_code"]
]

missing_descriptions = [
    record for record in transformed_records
    if not record["description"]
]

invalid_hashes = [
    record for record in transformed_records
    if len(record["desc_hash"]) != 32
]

codes = [
    record["hcpcs_code"]
    for record in transformed_records
]

duplicate_codes = {
    code for code in codes
    if codes.count(code) > 1
}

print("Missing codes:", len(missing_codes))
print("Missing descriptions:", len(missing_descriptions))
print("Invalid hash lengths:", len(invalid_hashes))
print("Duplicate HCPCS codes:", len(duplicate_codes))
print(transformed_records[:3])
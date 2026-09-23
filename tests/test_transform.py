import hashlib


def test_description_hash():
    description = "Ambulance service"

    expected_hash = hashlib.md5(
        description.encode("utf-8")
    ).hexdigest()

    actual_hash = hashlib.md5(
        description.encode("utf-8")
    ).hexdigest()

    assert actual_hash == expected_hash


def test_description_hash_is_32_characters():
    description = "Ambulance service"

    desc_hash = hashlib.md5(
        description.encode("utf-8")
    ).hexdigest()

    assert len(desc_hash) == 32


def test_record_has_required_fields():
    record = {
        "hcpcs_code": "A0021",
        "description": "Ambulance service"
    }

    assert record["hcpcs_code"]
    assert record["description"]


def test_duplicate_hcpcs_codes():
    records = [
        {"hcpcs_code": "A0021", "description": "Ambulance service"},
        {"hcpcs_code": "A0080", "description": "Non-emergency transportation"},
        {"hcpcs_code": "A0021", "description": "Ambulance service"}
    ]

    codes = [record["hcpcs_code"] for record in records]

    duplicates = {
        code for code in codes
        if codes.count(code) > 1
    }

    assert "A0021" in duplicates
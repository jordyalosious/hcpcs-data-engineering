import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def validate_data():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    cursor = connection.cursor()

    checks = {
        "null_hcpcs_codes": """
            SELECT COUNT(*)
            FROM hcpcs_codes
            WHERE hcpcs_code IS NULL;
        """,

        "null_descriptions": """
            SELECT COUNT(*)
            FROM hcpcs_codes
            WHERE long_description IS NULL;
        """,

        "duplicate_current_codes": """
            SELECT COUNT(*)
            FROM (
                SELECT hcpcs_code
                FROM hcpcs_codes
                WHERE is_current = TRUE
                GROUP BY hcpcs_code
                HAVING COUNT(*) > 1
            ) duplicates;
        """,

        "invalid_current_records": """
            SELECT COUNT(*)
            FROM hcpcs_codes
            WHERE is_current = TRUE
              AND end_date IS NOT NULL;
        """,

        "invalid_historical_records": """
            SELECT COUNT(*)
            FROM hcpcs_codes
            WHERE is_current = FALSE
              AND end_date IS NULL;
        """,

        "invalid_versions": """
            SELECT COUNT(*)
            FROM hcpcs_codes
            WHERE version < 1;
        """,

        "invalid_hashes": """
            SELECT COUNT(*)
            FROM hcpcs_codes
            WHERE desc_hash IS NULL
               OR LENGTH(desc_hash) <> 32;
        """,
    }

    validation_failed = False

    try:
        for check_name, query in checks.items():
            cursor.execute(query)
            result = cursor.fetchone()[0]

            print(f"{check_name}: {result}")

            if result > 0:
                validation_failed = True

        if validation_failed:
            print("DATA QUALITY FAILED")
            raise Exception("One or more data quality checks failed.")

        print("DATA QUALITY PASSED")

    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    validate_data()

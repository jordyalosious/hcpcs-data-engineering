import os
import json
import hashlib
from datetime import date

import psycopg2
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "raw/hcpcs_a_codes.json"

GROUP_CODE = "A"

CATEGORY_NAME = (
    "Transportation Services Including Ambulance, "
    "Medical & Surgical Supplies"
)


def calculate_hash(description):
    return hashlib.md5(
        description.encode("utf-8")
    ).hexdigest()


def load_data():

    # 1. Read JSON data
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    print("Records read from JSON:", len(records))

    # 2. Connect to PostgreSQL
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    cursor = connection.cursor()

    inserted_count = 0
    unchanged_count = 0
    updated_count = 0

    effective_date = date.today()

    try:

        # 3. Process each HCPCS record
        for record in records:

            hcpcs_code = record["hcpcs_code"].strip()
            description = record["description"].strip()

            desc_hash = calculate_hash(description)

            # 4. Check whether the current version already exists
            cursor.execute(
                """
                SELECT id, desc_hash, version
                FROM hcpcs_codes
                WHERE hcpcs_code = %s
                  AND is_current = TRUE
                """,
                (hcpcs_code,)
            )

            existing = cursor.fetchone()

            # 5. New HCPCS code
            if existing is None:

                cursor.execute(
                    """
                    INSERT INTO hcpcs_codes (
                        hcpcs_code,
                        group_code,
                        category_name,
                        long_description,
                        desc_hash,
                        effective_date,
                        end_date,
                        is_current,
                        version
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, NULL, TRUE, 1
                    )
                    """,
                    (
                        hcpcs_code,
                        GROUP_CODE,
                        CATEGORY_NAME,
                        description,
                        desc_hash,
                        effective_date,
                    )
                )

                inserted_count += 1

            # 6. Existing HCPCS code
            else:

                current_id, current_hash, current_version = existing

                # Description has not changed
                if current_hash == desc_hash:

                    unchanged_count += 1

                # Description has changed
                else:

                    # Expire old version
                    cursor.execute(
                        """
                        UPDATE hcpcs_codes
                        SET
                            end_date = %s,
                            is_current = FALSE
                        WHERE id = %s
                        """,
                        (effective_date, current_id)
                    )

                    # Insert new version
                    cursor.execute(
                        """
                        INSERT INTO hcpcs_codes (
                            hcpcs_code,
                            group_code,
                            category_name,
                            long_description,
                            desc_hash,
                            effective_date,
                            end_date,
                            is_current,
                            version
                        )
                        VALUES (
                            %s, %s, %s, %s, %s,
                            %s, NULL, TRUE, %s
                        )
                        """,
                        (
                            hcpcs_code,
                            GROUP_CODE,
                            CATEGORY_NAME,
                            description,
                            desc_hash,
                            effective_date,
                            current_version + 1,
                        )
                    )

                    updated_count += 1

        # 7. Commit everything
        connection.commit()

        print("Load completed successfully.")
        print("Inserted:", inserted_count)
        print("Unchanged:", unchanged_count)
        print("Updated:", updated_count)

    except Exception:

        # Roll back everything if something fails
        connection.rollback()

        print("Load failed. Transaction rolled back.")

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_data()
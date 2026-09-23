# HCPCS Data Engineering Pipeline

## 1. Project Overview

This project extracts HCPCS code data from a public website, cleans and validates it, and loads it into PostgreSQL. It also keeps historical versions of HCPCS descriptions using Slowly Changing Dimension Type 2 (SCD2). Apache Airflow handles the orchestration.

## 2. Architecture

text
HCPCS Website
      |
      v
Python Scraper
(requests + BeautifulSoup)
      |
      v
Raw JSON
(raw/hcpcs_a_codes.json)
      |
      v
Transformation
(normalization + desc_hash)
      |
      v
PostgreSQL
      |
      v
SCD Type 2 Load
      |
      v
Data Quality Validation
      |
      v
Airflow DAG
      |
      v
Success Notification


## 3. Tech Stack

- Python 3.x
- Requests
- BeautifulSoup
- Pandas
- PostgreSQL 18
- psycopg2
- Apache Airflow
- Docker / Docker Compose
- pytest
- python-dotenv
- Git

## 4. Data Source

Source: https://www.hcpcsdata.com/

I scraped the A-code category only.

- Group code: A
- Category: Transportation Services Including Ambulance, Medical & Surgical Supplies
- Records extracted: 862

## 5. Data Extraction

scraper/scraper.py

Uses requests to pull the page and BeautifulSoup to parse it. Records come from table rows with the clickable-row class. Each record has hcpcs_code and description.

Output: raw/hcpcs_a_codes.json

Result: HTTP 200, 862 records extracted.

## 6. Raw Data Staging

Raw scraped data is saved as JSON before it touches the database:

raw/hcpcs_a_codes.json

Keeps extraction separate from everything downstream, and gives me a snapshot to fall back on.

## 7. Transformation

transform/transform.py

Steps:
1. Read the raw JSON.
2. Trim whitespace from codes and descriptions.
3. Generate an MD5 hash of the description (desc_hash).
4. Run basic validation.

The hash is what SCD2 uses to detect description changes.

Validation checked for missing codes, missing descriptions, bad hash lengths, and duplicate codes.

Results: 862 transformed, 0 missing codes, 0 missing descriptions, 0 bad hashes, 0 duplicates.

## 8. PostgreSQL

PostgreSQL 18, running locally via Docker Compose.

- Database: hcpcs_db
- Main table: hcpcs_codes

## 9. Schema

| Column | Description |
|---|---|
| id | Surrogate primary key |
| hcpcs_code | HCPCS procedure/supply code |
| group_code | HCPCS group/category code |
| category_name | Category description |
| long_description | HCPCS description |
| desc_hash | MD5 hash of the description |
| effective_date | Start date of the record version |
| end_date | End date of the record version |
| is_current | Whether this is the current version |
| version | SCD2 version number |
| inserted_at | Record insertion timestamp |

Partial index on current records:

sql
CREATE INDEX idx_hcpcs_code_current
ON hcpcs_codes(hcpcs_code)
WHERE is_current;


## 10. SCD Type 2

database/load.py

Keeps a full history when a description changes instead of overwriting it.

Logic, per code:
1. If no current record exists, insert one with version = 1, is_current = TRUE.
2. If a current record exists, compare its desc_hash to the incoming one.
3. Same hash: no update needed.
4. Different hash: close the old record (set end_date, is_current = FALSE), insert a new version, bump the version number.

I tested this by manually changing one description. Result: 0 inserted, 861 unchanged, 1 updated. The old version stayed in the table as history, and a new current version was created. Reverted the test data afterward.

## 11. Data Quality Validation

database/validation.py, database/validation.sql

Checks:
1. NULL HCPCS codes
2. NULL descriptions
3. Duplicate current codes
4. Current records with an end date set (shouldn't happen)
5. Historical records missing an end date (shouldn't happen)
6. Invalid version numbers
7. Invalid hash lengths

Latest run: everything came back 0. Data quality passed.

## 12. Airflow

dags/hcpcs_pipeline.py, DAG name: hcpcs_data_pipeline

Tasks run in order:

text
extract -> transform -> load_scd2 -> validate -> notify


| Task | Purpose |
|---|---|
| extract | Pull HCPCS data from the source site |
| transform | Normalize data, generate hashes |
| load_scd2 | Load into Postgres with SCD2 logic |
| validate | Run data quality checks |
| notify | Report pipeline success |

Scheduled to run daily.

## 13. Docker

PostgreSQL runs in Docker via docker-compose.yml, exposed on localhost:5432.

- Database: hcpcs_db
- User: postgres
- Password comes from environment config, not committed to Git.

## 14. Environment Config

env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hcpcs_db
DB_USER=postgres
DB_PASSWORD=your_password_here


Example lives in .env.example. The real .env is gitignored.

## 15. Testing

tests/test_transform.py

Covers hash generation, hash length, required fields, and duplicate detection.

Current result: 4 passed.

Run with:

bash
pytest


## 16. Running the Project

bash
# 1. Clone
git clone <repository-url>
cd hcpcs-data-engineering

# 2. Set up env
cp .env.example .env
# fill in your PostgreSQL credentials

# 3. Start Postgres
docker compose up -d

# 4. Check it's ready
docker exec hcpcs-postgres pg_isready -U postgres -d hcpcs_db

# 5. Create the table
# run database/schema.sql against hcpcs_db

# 6. Extract
python scraper/scraper.py

# 7. Transform
python transform/transform.py

# 8. Load
python database/load.py

# 9. Validate
python database/validation.py

# 10. Test
pytest


Or run it all through the hcpcs_data_pipeline Airflow DAG.

## 17. Sample Queries

Count current records:

sql
SELECT COUNT(*)
FROM hcpcs_codes
WHERE is_current = TRUE;


List current codes:

sql
SELECT hcpcs_code, long_description, version, effective_date
FROM hcpcs_codes
WHERE is_current = TRUE
ORDER BY hcpcs_code;


Full history for one code:

sql
SELECT hcpcs_code, long_description, version, effective_date, end_date, is_current
FROM hcpcs_codes
WHERE hcpcs_code = 'A0021'
ORDER BY version;


Check for duplicate current records:

sql
SELECT hcpcs_code, COUNT(*) AS duplicate_count
FROM hcpcs_codes
WHERE is_current = TRUE
GROUP BY hcpcs_code
HAVING COUNT(*) > 1;


## 18. Project Structure

text
hcpcs-data-engineering/
│
├── dags/
│   └── hcpcs_pipeline.py
│
├── database/
│   ├── load.py
│   ├── schema.sql
│   ├── validation.py
│   └── validation.sql
│
├── raw/
│   └── hcpcs_a_codes.json
│
├── scraper/
│   └── scraper.py
│
├── tests/
│   └── test_transform.py
│
├── transform/
│   └── transform.py
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
├── requirements.txt
└── logs/


## 19. Scope

This covers the HCPCS A-code category only (862 records), not the full HCPCS code set. The scraper and metadata mapping could be extended to other categories. Right now everything runs against a local Postgres instance — for production scale I'd look at moving storage and processing to a cloud data warehouse.

## 20. Summary

End to end, this covers: scraping the source site, staging raw data, transforming and hashing it, loading into Postgres with SCD2 history tracking, running data quality checks, and orchestrating the whole thing with Airflow — plus tests, Docker for local dev, and env-based config.
-- 1. Check for NULL HCPCS codes
SELECT COUNT(*) AS null_hcpcs_codes
FROM hcpcs_codes
WHERE hcpcs_code IS NULL;


-- 2. Check for NULL descriptions
SELECT COUNT(*) AS null_descriptions
FROM hcpcs_codes
WHERE long_description IS NULL;


-- 3. Check for duplicate current HCPCS codes
SELECT
    hcpcs_code,
    COUNT(*) AS duplicate_count
FROM hcpcs_codes
WHERE is_current = TRUE
GROUP BY hcpcs_code
HAVING COUNT(*) > 1;


-- 4. Check current records with an end date
SELECT COUNT(*) AS invalid_current_records
FROM hcpcs_codes
WHERE is_current = TRUE
  AND end_date IS NOT NULL;


-- 5. Check historical records that are still marked current
SELECT COUNT(*) AS invalid_historical_records
FROM hcpcs_codes
WHERE is_current = FALSE
  AND end_date IS NULL;


-- 6. Check invalid versions
SELECT COUNT(*) AS invalid_versions
FROM hcpcs_codes
WHERE version < 1;


-- 7. Check records with invalid hash length
SELECT COUNT(*) AS invalid_hashes
FROM hcpcs_codes
WHERE desc_hash IS NULL
   OR LENGTH(desc_hash) <> 32;
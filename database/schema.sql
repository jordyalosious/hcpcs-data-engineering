CREATE TABLE hcpcs_codes (
 id BIGSERIAL PRIMARY KEY,
 hcpcs_code VARCHAR(50) NOT NULL,
 group_code VARCHAR(10),
 category_name VARCHAR(255),
 long_description TEXT,
 desc_hash CHAR(32),
 effective_date DATE,
 end_date DATE,
 is_current BOOLEAN DEFAULT true,
 version INT DEFAULT 1,
 inserted_at TIMESTAMP DEFAULT now()
);
CREATE INDEX idx_hcpcs_code_current ON hcpcs_codes(hcpcs_code) WHERE is_current;
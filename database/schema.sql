CREATE TABLE IF NOT EXISTS data_centres (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    operator         TEXT NOT NULL,
    city             TEXT NOT NULL,
    province         TEXT NOT NULL,
    province_full    TEXT NOT NULL,
    address          TEXT,
    latitude         REAL NOT NULL,
    longitude        REAL NOT NULL,
    size_category    TEXT NOT NULL
        CHECK(size_category IN ('hyperscale','enterprise','colocation','edge')),
    floor_space_sqft INTEGER,
    power_mw         REAL,
    year_established INTEGER,
    tier_rating      TEXT,
    certifications   TEXT,
    operator_url     TEXT,
    created_at       TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_province ON data_centres(province);
CREATE INDEX IF NOT EXISTS idx_operator ON data_centres(operator);
CREATE INDEX IF NOT EXISTS idx_size     ON data_centres(size_category);

CREATE VIEW IF NOT EXISTS dc_summary AS
SELECT province, province_full, size_category, COUNT(*) AS count,
       AVG(power_mw) AS avg_power_mw
FROM data_centres GROUP BY province, size_category;

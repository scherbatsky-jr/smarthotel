CREATE TABLE IF NOT EXISTS raw_data (
  timestamp   INTEGER NOT NULL,
  datetime    TIMESTAMPTZ NOT NULL,
  device_id   TEXT NOT NULL,
  datapoint   TEXT NOT NULL,
  value       TEXT NOT NULL
);

-- Convert to hypertable
SELECT create_hypertable('raw_data', 'datetime', if_not_exists => TRUE);

-- Create table for EEG data
CREATE TABLE eeg_data (
    timestamp TIMESTAMPTZ PRIMARY KEY,
    fp1 DOUBLE PRECISION,
    fz DOUBLE PRECISION,
    f3 DOUBLE PRECISION,
    f7 DOUBLE PRECISION,
    ft9 DOUBLE PRECISION,
    fc5 DOUBLE PRECISION,
    fc1 DOUBLE PRECISION,
    c3 DOUBLE PRECISION,
    t7 DOUBLE PRECISION,
    tp9 DOUBLE PRECISION,
    cp5 DOUBLE PRECISION,
    cp1 DOUBLE PRECISION,
    pz DOUBLE PRECISION,
    p3 DOUBLE PRECISION,
    p7 DOUBLE PRECISION,
    o1 DOUBLE PRECISION,
    oz DOUBLE PRECISION,
    o2 DOUBLE PRECISION,
    p4 DOUBLE PRECISION,
    p8 DOUBLE PRECISION,
    tp10 DOUBLE PRECISION,
    cp6 DOUBLE PRECISION,
    cp2 DOUBLE PRECISION,
    cz DOUBLE PRECISION,
    c4 DOUBLE PRECISION,
    t8 DOUBLE PRECISION,
    ft10 DOUBLE PRECISION,
    fc6 DOUBLE PRECISION,
    fc2 DOUBLE PRECISION,
    f4 DOUBLE PRECISION,
    f8 DOUBLE PRECISION,
    fp2 DOUBLE PRECISION,
    x_dir INTEGER,
    y_dir INTEGER,
    z_dir INTEGER,
    mkidx DOUBLE PRECISION
);

-- Convert the table to a TimescaleDB hypertable
SELECT create_hypertable('eeg_data', by_range('timestamp', INTERVAL '10 minutes'));

-- Add a retention policy to the hypertable to make sure that data older than 120 minutes is automatically dropped
SELECT add_retention_policy('eeg_data', drop_after => INTERVAL '120 minutes', schedule_interval => INTERVAL '10 minutes');
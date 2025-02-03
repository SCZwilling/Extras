CREATE TABLE "fdxm_data" (
    "machine_id" int4,
    "machine_obj_name" VARCHAR(500),
    "shopfloor_id" int4,
    "room_id" int4,
    "room_obj_name" VARCHAR(500),
    "mac_address" TEXT,
    "time" TIMESTAMPTZ,  -- Time column for hypertable

    -- "local_timestamp" TIMESTAMP,
    "xrays" text,
    "target_voltage" FLOAT,
    "target_power" FLOAT,
    "target_current" FLOAT,
    "interlock" text,
    "status" text,

    "live_sample_x" text,
    "live_sample_y" text,
    "live_sample_z" text,
    "sample_theta" text,
    "dector" text,
    "source" text,
    "filter" text,
    "voltage" text,
    "power" text,
    "fov" text,
    "fov_2" text,
    "pixel_size" FLOAT,
    "obj" text,
    -- "binning" INTEGER,
    "exposure" text,
    "cone_angle" text,
    "fan_angle" text,

    "name" text,
    "source_power" text,
    "sample_x" text,
    "sample_y" text,
    "sample_z" text,
    "mode" text,
    "bin" INTEGER,
    "exp" text,
    "src_z" FLOAT,
    "det_z" FLOAT,
    "remainingtime" text,
    "projection" text
    
    -- "parameter_value" text,
    --"parameter" text,
    -- "logs"
    -- "top_y_pos" FLOAT,
    -- "bottom_y_pos" FLOAT
);
SELECT create_hypertable('fdxm_data', 'time');
ALTER TABLE "fdxm_data" ADD FOREIGN KEY ("mac_address") REFERENCES "devices" ("mac_address");
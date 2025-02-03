CREATE TABLE "mpu_burst" (
    "machine_id" int4,
    "machine_obj_name" VARCHAR(500),
    "shopfloor_id" int4,
    "room_id" int4,
    "room_obj_name" VARCHAR(500),
    "mac_address" TEXT,
    "time" TIMESTAMPTZ,
    "batch_id" INTEGER,
    "ax" Float,
    "ay" Float,
    "az" Float,
    "gx" Float,
    "gy" Float,
    "gz" Float,
    "mx" Float,
    "my" Float,
    "mz" Float,
    "sensor_id" INTEGER
)

SELECT create_hypertable('mpu_burst', 'time');
ALTER TABLE "mpu_burst" ADD FOREIGN KEY ("mac_address") REFERENCES "devices" ("mac_address");
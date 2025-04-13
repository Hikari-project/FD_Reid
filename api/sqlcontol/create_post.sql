-- 创建 ai_boxs 表
CREATE TABLE ai_boxs (
    id SERIAL PRIMARY KEY,
    ip VARCHAR(45),
    mask VARCHAR(45),
    gateway VARCHAR(45),
    upload_data VARCHAR(45),
    target_server VARCHAR(45),
    power_time TIMESTAMP,
    shutdown_time TIMESTAMP,
    describe TEXT,
    img VARCHAR(45)
);

-- 创建 rtsps 表
CREATE TABLE rtsps (
    id SERIAL PRIMARY KEY,
    box_id INTEGER REFERENCES ai_boxs(id),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

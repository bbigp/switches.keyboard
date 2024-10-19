CREATE TABLE IF NOT EXISTS icgb (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    href TEXT,
    icgb_day TEXT,
    day TEXT,
    text TEXT,
    unique_title TEXT,
    url TEXT NOT NULL,
    create_time INTEGER,
    update_time INTEGER,
    deleted INTEGER DEFAULT 0,
    usefulness INTEGER DEFAULT 0,
    UNIQUE(unique_title, url)
);
CREATE TABLE IF NOT EXISTS board (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sid BIGINT NOT NULL,
    row INT NOT NULL,
    col INT NOT NULL,
    ref TEXT NOT NULL,
    UNIQUE(ref, row, col)
);

CREATE TABLE integration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
    sql_script TEXT NOT NULL DEFAULT '',   -- 存储 SQL 变更脚本
    applied_at INTEGER,                    -- 时间戳，记录变更应用的时间
    status INTEGER DEFAULT 0               -- 变更状态，默认值为 0
);

update switches set type = '提前段落轴' where type = '提前大段落轴'

update switches set manufacturer = '' where manufacturer is null
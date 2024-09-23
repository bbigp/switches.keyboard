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
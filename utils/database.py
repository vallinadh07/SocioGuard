import sqlite3

# ---------- CREATE DB ----------
def init_db():
    conn = sqlite3.connect("socioguard.db")
    cursor = conn.cursor()

    # ✅ Existing table (unchanged)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        link TEXT,
        risk TEXT,
        score INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 🔥 NEW TABLE (Behavior Tracking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_behavior (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        risky_count INTEGER DEFAULT 0,
        safe_count INTEGER DEFAULT 0
    )
    """)

    # 🔥 Ensure default row exists
    cursor.execute("SELECT COUNT(*) FROM user_behavior")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO user_behavior (risky_count, safe_count)
        VALUES (0, 0)
        """)

    # 🔥🔥 NEW TABLE (SCAM PATTERN MEMORY - ABTIS STEP 1)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scam_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT UNIQUE,
        count INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


# ---------- SAVE DATA ----------
def save_scan(message, link, risk, score):
    conn = sqlite3.connect("socioguard.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO scans (message, link, risk, score)
    VALUES (?, ?, ?, ?)
    """, (message, link, risk, score))

    conn.commit()
    conn.close()


# ---------- FETCH DATA ----------
def get_history():
    conn = sqlite3.connect("socioguard.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scans ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()
    return data


# ---------- STATS ----------
def get_stats():
    conn = sqlite3.connect("socioguard.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM scans")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scans WHERE risk='HIGH'")
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM scans WHERE risk='SAFE'")
    safe = cursor.fetchone()[0]

    conn.close()

    return total, high, safe


# 🔥 ---------- BEHAVIOR TRACKING ----------

def update_behavior(risk):
    conn = sqlite3.connect("socioguard.db")
    cursor = conn.cursor()

    if risk == "HIGH":
        cursor.execute("""
        UPDATE user_behavior
        SET risky_count = risky_count + 1
        WHERE id = 1
        """)
    else:
        cursor.execute("""
        UPDATE user_behavior
        SET safe_count = safe_count + 1
        WHERE id = 1
        """)

    conn.commit()
    conn.close()


def get_behavior():
    conn = sqlite3.connect("socioguard.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT risky_count, safe_count
    FROM user_behavior
    WHERE id = 1
    """)

    data = cursor.fetchone()

    conn.close()
    return data


# 🔥🔥 ---------- ABTIS STEP 1 FUNCTIONS ----------

def save_pattern(keyword):
    conn = sqlite3.connect("socioguard.db")
    cursor = conn.cursor()

    cursor.execute("SELECT count FROM scam_patterns WHERE keyword=?", (keyword,))
    result = cursor.fetchone()

    if result:
        cursor.execute(
            "UPDATE scam_patterns SET count = count + 1 WHERE keyword=?",
            (keyword,)
        )
    else:
        cursor.execute(
            "INSERT INTO scam_patterns (keyword, count) VALUES (?, 1)",
            (keyword,)
        )

    conn.commit()
    conn.close()


def get_top_patterns():
    conn = sqlite3.connect("socioguard.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT keyword, count FROM scam_patterns
    ORDER BY count DESC LIMIT 5
    """)

    data = cursor.fetchall()
    conn.close()
    return data
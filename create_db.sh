sqlite3 example.db << EOF
CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY,
                amount INTEGER NOT NULL
            )
EOF
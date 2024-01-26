import json


def setup_database(conn):
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_smiles (
                user_id TEXT PRIMARY KEY,
                smiles TEXT
            )
        """)


def save_data(conn, user_id, smiles):
    with conn:
        conn.execute("REPLACE INTO user_smiles (user_id, smiles) VALUES (?, ?)",
                     (user_id, json.dumps(smiles)))


def load_data(conn, user_id):
    with conn:
        cur = conn.execute("SELECT smiles FROM user_smiles WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return []


def get_all_user_ids(conn):
    with conn:
        cur = conn.execute("SELECT user_id FROM user_smiles")
        return [row[0] for row in cur.fetchall()]

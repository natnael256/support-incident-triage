

import json
import os
import sys 

import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


load_dotenv()

INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else "tickets.json"


COLUMNS = [
    "external_id",
    "source",
    "created_at",
    "title",
    "body",
    "service",
    "status",
    "raw",
]

COLUMN_LIST = ", ".join(COLUMNS)

INSERT_SQL = f"""
    INSERT INTO incidents ({COLUMN_LIST})
    VALUES %s
    ON CONFLICT (external_id) DO UPDATE SET
        source     = EXCLUDED.source,
        created_at = EXCLUDED.created_at,
        title      = EXCLUDED.title,
        body       = EXCLUDED.body,
        service    = EXCLUDED.service,
        status     = EXCLUDED.status,
        raw        = EXCLUDED.raw
"""

def load_tickets(path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        raise SystemExit(
            f"{path} is a json object, expected a list. " "check the generator's output shape."

        )

    return data

def to_row(ticket):
    try:
        return (
            ticket["external_id"],
            ticket["source"],
            ticket["created_at"],
            ticket["title"],
            ticket["body"],
            ticket["service"],
            ticket["status"],
            json.dumps(ticket), 

        )
    except KeyError as e:
        raise SystemExit(
            f"Ticket missing required field {e}: "
            f"{ticket.get('external_id', '<no external_id>')}"
        )
 

def main():

    tickets = load_tickets(INPUT_FILE)
    rows = [to_row(t) for t in tickets]

    ids = [r[0] for r in rows]

    if len(set(ids)) != len(ids):
        print(
            f" WARNING: {len(ids) - len(set(ids))} duplicate external_id values"
            " in the input. Later row will over write earlier ones.", 
            file = sys.stderr, 

        )
    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


    try: 
        with conn: 
            with conn.cursor() as cur:
                execute_values(cur, INSERT_SQL, rows,page_size = 500)

            print(f"Ingested {len(rows)} tickets from {INPUT_FILE}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
    
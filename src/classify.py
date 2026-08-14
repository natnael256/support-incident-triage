#!/usr/bin/env python3


import os
import sys
from collections import Counter

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from dotenv import load_dotenv

from rules import load_rules, classify

load_dotenv()

RULES_FILE = sys.argv[1] if len(sys.argv) > 1 else "../rules.yaml"


def main():
    rules = load_rules(RULES_FILE)

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT external_id, title, body FROM incidents "
                    "WHERE severity IS NULL"
                )
                tickets = cur.fetchall()

            if not tickets:
                print("No unclassified incidents.")
                return

            results = []
            counts = Counter()
            for j in tickets:
                severity, rule_name = classify(j, rules)
                counts[rule_name] += 1
                if severity is not None:
                    results.append((j["external_id"], severity, rule_name))

            if results:
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        """
                        UPDATE incidents SET severity = v.severity,
                                             matched_rule = v.matched_rule
                        FROM (VALUES %s) AS v(external_id, severity, matched_rule)
                        WHERE incidents.external_id = v.external_id
                        """,
                        results,
                        page_size=500,
                    )

        total = len(tickets)
        matched = len(results)
        pct = matched / total if total else 0
        print(f"Classified {matched}/{total} ({pct:.1%} coverage)\n")
        for name, n in counts.most_common():
            label = name if name else "UNMATCHED"
            print(f"  {label:<28} {n}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
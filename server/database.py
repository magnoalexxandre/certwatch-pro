import os
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import List, Dict

DATABASE_URL = os.getenv("DATABASE_URL")
_pool = None


def init_db():
    global _pool
    _pool = SimpleConnectionPool(1, 10, DATABASE_URL)
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS certificates (
                    id          SERIAL PRIMARY KEY,
                    hostname    VARCHAR(255) NOT NULL,
                    path        TEXT NOT NULL,
                    subject     TEXT,
                    issuer      TEXT,
                    not_before  TEXT,
                    not_after   TEXT,
                    days_remaining INTEGER,
                    serial_number  TEXT,
                    fingerprint    VARCHAR(64),
                    cert_type      VARCHAR(50),
                    last_update    TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_cert_hostname
                    ON certificates(hostname);
                CREATE INDEX IF NOT EXISTS idx_cert_days
                    ON certificates(days_remaining);
            """)


@contextmanager
def _get_conn():
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


def upsert_report(hostname: str, certificates: List[Dict], timestamp: str):
    with _get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM certificates WHERE hostname = %s", (hostname,))
            for cert in certificates:
                cur.execute("""
                    INSERT INTO certificates
                        (hostname, path, subject, issuer, not_before, not_after,
                         days_remaining, serial_number, fingerprint, cert_type, last_update)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    hostname,
                    cert["path"],
                    cert["subject"],
                    cert["issuer"],
                    cert["not_before"],
                    cert["not_after"],
                    cert["days_remaining"],
                    cert["serial_number"],
                    cert["fingerprint"],
                    cert["cert_type"],
                    timestamp,
                ))


def get_all_certificates() -> List[Dict]:
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM certificates ORDER BY days_remaining")
            return [dict(row) for row in cur.fetchall()]


def get_stats() -> Dict:
    certs = get_all_certificates()
    total = len(certs)
    expired  = sum(1 for c in certs if c["days_remaining"] < 0)
    critical = sum(1 for c in certs if 0 <= c["days_remaining"] <= 10)
    warning  = sum(1 for c in certs if 10 < c["days_remaining"] <= 20)
    ok = total - expired - critical - warning
    return {
        "total": total,
        "expired": expired,
        "critical": critical,
        "warning": warning,
        "ok": ok,
        "hosts": len(set(c["hostname"] for c in certs)),
    }


def get_agent_status() -> List[Dict]:
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT hostname, MAX(last_update) AS last_seen, COUNT(*) AS cert_count
                FROM certificates
                GROUP BY hostname
                ORDER BY hostname
            """)
            return [dict(row) for row in cur.fetchall()]

# connect.py – Thin wrapper around psycopg2 connection

import psycopg2
import psycopg2.extras
from config import DB_CONFIG


def get_connection():
    """Return a new psycopg2 connection using DB_CONFIG."""
    return psycopg2.connect(**DB_CONFIG)


def get_cursor(conn):
    """Return a DictCursor for the given connection."""
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
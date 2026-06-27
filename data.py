from decimal import Decimal, ROUND_HALF_UP
import sqlite3
import streamlit as st

DB_PATH = "fintrack.db"


def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_type TEXT,
        category TEXT,
        amount REAL,
        importance TEXT,
        date TEXT
    )
    """)
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [row[1] for row in cursor.fetchall()]
    if "date" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN date TEXT")
    conn.commit()
    conn.close()


def save_transaction(transaction_type, category, amount, importance, date):
    amount = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transactions (transaction_type, category, amount, importance, date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (transaction_type, category, amount, importance, date),
    )
    conn.commit()
    conn.close()


def get_transactions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [row[1] for row in cursor.fetchall()]
    if "date" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN date TEXT")
        conn.commit()
    cursor.execute("""SELECT id, transaction_type, category, amount, date FROM transactions ORDER BY id DESC""")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_transaction(transaction_id, transaction_type, category, amount, date):
    amount = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE transactions
        SET transaction_type = ?, category = ?, amount = ?, date = ?
        WHERE id = ?
        """,
        (transaction_type, category, amount, date, transaction_id),
    )
    conn.commit()
    conn.close()


def get_total_expenses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE transaction_type='Debit'"""
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_total_credits():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE transaction_type='Credit'"""
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total
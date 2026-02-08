import sqlite3
DB_NAME = "expenses.db"
def create_db():
    """
    Create expenses table if it does not exist.
    """

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                description TEXT,
                amount REAL,
                payment_mode TEXT
            )
        """)

        conn.commit()
        conn.close()

    except Exception as e:
        print("Database creation error:", e)
def add_expense(date, category, description, amount, payment_mode):
    """
    Insert new expense record into database.
    """

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expenses
            (date, category, description, amount, payment_mode)
            VALUES (?, ?, ?, ?, ?)
        """, (date, category, description, amount, payment_mode))

        conn.commit()
        conn.close()

    except Exception as e:
        print("Insert error:", e)
def get_expenses():
    """
    Fetch all expenses from database.
    """

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = cursor.fetchall()

        conn.close()

        return rows

    except Exception as e:
        print("Fetch error:", e)
        return []

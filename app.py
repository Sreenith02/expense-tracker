"""
Expense Tracker
---------------
A simple expense tracking web application built with:
  * Streamlit -> user interface
  * SQLite    -> permanent storage (file: expenses.db)
  * Pandas    -> data handling
  * Plotly    -> interactive charts

Run with:  streamlit run app.py
"""

import math
import os
import random
import sqlite3
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "expenses.db")
CURRENCY = "$"  # Change this symbol if you want a different currency
CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]
MAX_AMOUNT = 1_000_000
MAX_DESCRIPTION_LENGTH = 200
EARLIEST_DATE = date(1900, 1, 1)
LATEST_DATE = date(9999, 12, 31)

# Must be the first Streamlit command in the file
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")

# Modern look: coloured gradient cards for the dashboard metrics
st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    div[data-testid="stMetric"] * {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Database functions
# ----------------------------------------------------------------------------
def get_connection():
    """Open a connection to the SQLite database file."""
    return sqlite3.connect(DB_FILE)


def init_db():
    """Create the expenses table the first time the app runs."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                amount       REAL    NOT NULL CHECK (amount > 0),
                category     TEXT    NOT NULL,
                expense_date TEXT    NOT NULL,
                description  TEXT    NOT NULL DEFAULT ''
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def execute_write(sql, params=()):
    """Run an INSERT, UPDATE or DELETE using parameters (?) for safety."""
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def load_expenses(category, start_date, end_date):
    """Return expenses as a Pandas DataFrame, filtered by category and date."""
    sql = """
        SELECT id, amount, category, expense_date, description
        FROM expenses
        WHERE expense_date BETWEEN ? AND ?
    """
    params = [start_date.isoformat(), end_date.isoformat()]

    if category != "All":
        sql += " AND category = ?"
        params.append(category)

    sql += " ORDER BY expense_date DESC, id DESC"

    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()

    df["description"] = df["description"].fillna("")
    return df


def count_expenses():
    """Return how many expense records are stored."""
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    finally:
        conn.close()


def insert_demo_data():
    """Insert 40 random sample expenses from the last 120 days."""
    rng = random.Random(42)  # fixed seed so the demo is repeatable
    samples = {
        "Food": ["Lunch at canteen", "Groceries", "Pizza night", "Coffee"],
        "Transport": ["Bus pass", "Taxi to campus", "Fuel", "Train ticket"],
        "Shopping": ["New shoes", "Headphones", "Stationery", "Clothes"],
        "Bills": ["Electricity bill", "Internet bill", "Phone recharge"],
        "Entertainment": ["Movie tickets", "Concert", "Streaming subscription"],
        "Health": ["Pharmacy", "Gym membership", "Doctor visit"],
        "Education": ["Textbook", "Online course", "Printing notes"],
        "Other": ["Gift for friend", "Donation", "Miscellaneous"],
    }

    today = date.today()
    rows = []
    for _ in range(40):
        category = rng.choice(CATEGORIES)
        description = rng.choice(samples[category])
        amount = round(rng.uniform(3, 180), 2)
        expense_date = today - timedelta(days=rng.randint(0, 120))
        rows.append((amount, category, expense_date.isoformat(), description))

    conn = get_connection()
    try:
        conn.executemany(
            """
            INSERT INTO expenses (amount, category, expense_date, description)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()
    finally:
        conn.close()


# ----------------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------------
def validate_expense(amount, category, expense_date, description):
    """Check the input values and return a list of error messages."""
    errors = []

    if not math.isfinite(amount) or amount <= 0:
        errors.append("Amount must be a number greater than 0.")
    elif amount > MAX_AMOUNT:
        errors.append(f"Amount cannot be more than {CURRENCY}{MAX_AMOUNT:,}.")

    if category not in CATEGORIES:
        errors.append("Please choose a valid category.")

    if expense_date > date.today():
        errors.append("The date cannot be in the future.")

    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            f"Description must be {MAX_DESCRIPTION_LENGTH} characters or fewer."
        )

    return errors


def set_flash(kind, message):
    """Save a message that will be shown after the page refreshes."""
    st.session_state["flash"] = (kind, message)


def show_flash():
    """Show the saved message (if any) and then clear it."""
    if "flash" in st.session_state:
        kind, message = st.session_state.pop("flash")
        if kind == "success":
            st.success(message)
        elif kind == "warning":
            st.warning(message)
        else:
            st.error(message)


# ----------------------------------------------------------------------------
# Page sections
# ----------------------------------------------------------------------------
def sidebar_section():
    """Show filters and data tools in the sidebar. Returns the filter values."""
    with st.sidebar:
        st.header("🔍 Filters")
        st.caption("Filters apply to the Dashboard.")
        category = st.selectbox("Category", ["All"] + CATEGORIES)
        start_date = st.date_input(
            "From date",
            value=date.today() - timedelta(days=365),
            max_value=date.today(),
        )
        end_date = st.date_input(
            "To date",
            value=date.today(),
            max_value=date.today(),
        )

        st.divider()
        st.header("🧪 Data tools")

        if st.button("Load demo data", use_container_width=True):
            if count_expenses() > 0:
                set_flash(
                    "warning",
                    "The database already has expenses. Clear all data first "
                    "if you want to load the demo data again.",
                )
            else:
                insert_demo_data()
                set_flash("success", "40 demo expenses were loaded!")
            st.rerun()

        confirm_clear = st.checkbox("I want to delete ALL expenses")
        if st.button("Clear all data", disabled=not confirm_clear, use_container_width=True):
            execute_write("DELETE FROM expenses")
            set_flash("success", "All expenses were deleted.")
            st.rerun()

    return category, start_date, end_date


def add_expense_section():
    """Form for adding a new expense."""
    st.subheader("Add a new expense")

    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        amount = col1.number_input("Amount", min_value=0.0, step=1.0, format="%.2f")
        category = col2.selectbox("Category", CATEGORIES)

        col3, col4 = st.columns(2)
        expense_date = col3.date_input("Date", value=date.today(), max_value=date.today())
        description = col4.text_input(
            "Description (optional)",
            max_chars=MAX_DESCRIPTION_LENGTH,
            placeholder="e.g. Lunch with friends",
        )

        submitted = st.form_submit_button("➕ Add Expense", type="primary")

    if submitted:
        amount = round(float(amount), 2)
        description = description.strip()
        errors = validate_expense(amount, category, expense_date, description)

        if errors:
            for error in errors:
                st.error(error)
        else:
            execute_write(
                """
                INSERT INTO expenses (amount, category, expense_date, description)
                VALUES (?, ?, ?, ?)
                """,
                (amount, category, expense_date.isoformat(), description),
            )
            set_flash(
                "success",
                f"Expense of {CURRENCY}{amount:,.2f} added under {category}.",
            )
            st.rerun()


def edit_delete_section():
    """Choose an expense, then edit or delete it."""
    st.subheader("Edit or delete an expense")

    all_df = load_expenses("All", EARLIEST_DATE, LATEST_DATE)
    if all_df.empty:
        st.info(
            "No expenses yet. Add one in the Add Expense tab, "
            "or load demo data from the sidebar."
        )
        return

    labels = {
        int(r.id): (
            f"#{int(r.id)} | {r.expense_date} | {r.category} | "
            f"{CURRENCY}{r.amount:,.2f} | {r.description or 'no description'}"
        )
        for r in all_df.itertuples()
    }
    ids = all_df["id"].astype(int).tolist()

    selected_id = st.selectbox(
        "Select an expense",
        ids,
        format_func=lambda i: labels[i],
        key="edit_select",
    )
    expense_id = int(selected_id)
    row = all_df.loc[all_df["id"] == selected_id].iloc[0]

    # Keys include the expense id, so the form shows the selected record's values
    with st.form(f"edit_form_{expense_id}"):
        col1, col2 = st.columns(2)
        amount = col1.number_input(
            "Amount",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            value=float(row["amount"]),
            key=f"edit_amount_{expense_id}",
        )
        current_category = row["category"] if row["category"] in CATEGORIES else "Other"
        category = col2.selectbox(
            "Category",
            CATEGORIES,
            index=CATEGORIES.index(current_category),
            key=f"edit_category_{expense_id}",
        )

        col3, col4 = st.columns(2)
        expense_date = col3.date_input(
            "Date",
            value=date.fromisoformat(row["expense_date"]),
            max_value=date.today(),
            key=f"edit_date_{expense_id}",
        )
        description = col4.text_input(
            "Description (optional)",
            value=row["description"],
            max_chars=MAX_DESCRIPTION_LENGTH,
            key=f"edit_description_{expense_id}",
        )

        save = st.form_submit_button("💾 Save Changes", type="primary")

    if save:
        amount = round(float(amount), 2)
        description = description.strip()
        errors = validate_expense(amount, category, expense_date, description)

        if errors:
            for error in errors:
                st.error(error)
        else:
            execute_write(
                """
                UPDATE expenses
                SET amount = ?, category = ?, expense_date = ?, description = ?
                WHERE id = ?
                """,
                (amount, category, expense_date.isoformat(), description, expense_id),
            )
            set_flash("success", "Expense updated successfully.")
            st.rerun()

    st.markdown("#### Delete this expense")
    confirm_delete = st.checkbox(
        "Yes, I want to permanently delete this expense",
        key=f"confirm_delete_{expense_id}",
    )
    if st.button("🗑️ Delete Expense", disabled=not confirm_delete, key=f"delete_{expense_id}"):
        execute_write("DELETE FROM expenses WHERE id = ?", (expense_id,))
        set_flash("success", "Expense deleted.")
        st.rerun()


def dashboard_section(df):
    """Show metric cards, charts, category totals and the expense table."""
    if df.empty:
        st.info(
            "No expenses match the current filters. Change the filters in the "
            "sidebar, or add a new expense."
        )
        return

    total = df["amount"].sum()
    count = len(df)
    average = df["amount"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Total Expenses", f"{CURRENCY}{total:,.2f}")
    col2.metric("🧾 Number of Transactions", f"{count:,}")
    col3.metric("📈 Average Expense", f"{CURRENCY}{average:,.2f}")

    category_totals = (
        df.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )

    left, right = st.columns(2)
    pie = px.pie(
        category_totals,
        names="category",
        values="amount",
        title="Spending Share by Category",
        hole=0.4,
    )
    bar = px.bar(
        category_totals,
        x="category",
        y="amount",
        color="category",
        title="Total Spent per Category",
        text_auto=".2f",
    )
    left.plotly_chart(pie, use_container_width=True)
    right.plotly_chart(bar, use_container_width=True)

    st.subheader("Category-wise totals")
    st.dataframe(
        category_totals.rename(columns={"category": "Category", "amount": "Total"}),
        use_container_width=True,
        hide_index=True,
        column_config={"Total": st.column_config.NumberColumn(format=f"{CURRENCY}%.2f")},
    )

    st.subheader("All expenses (after filters)")
    table = df.rename(
        columns={
            "id": "ID",
            "amount": "Amount",
            "category": "Category",
            "expense_date": "Date",
            "description": "Description",
        }
    )
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={"Amount": st.column_config.NumberColumn(format=f"{CURRENCY}%.2f")},
    )

    st.download_button(
        "⬇️ Download as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="expenses.csv",
        mime="text/csv",
    )


# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------
def main():
    init_db()

    st.title("💰 Expense Tracker")
    st.caption("Track your spending, see where your money goes, and keep everything saved in expenses.db")

    show_flash()

    category, start_date, end_date = sidebar_section()

    tab_dashboard, tab_add, tab_edit = st.tabs(
        ["📊 Dashboard", "➕ Add Expense", "✏️ Edit / Delete"]
    )

    with tab_dashboard:
        if start_date > end_date:
            st.warning("'From date' must be before 'To date'.")
        else:
            df = load_expenses(category, start_date, end_date)
            dashboard_section(df)

    with tab_add:
        add_expense_section()

    with tab_edit:
        edit_delete_section()


main()

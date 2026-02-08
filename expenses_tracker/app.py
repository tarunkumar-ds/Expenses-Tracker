import streamlit as st
import pandas as pd
import datetime
import sqlite3
import io
from database import create_db, add_expense, get_expenses
DB_NAME = "expenses.db"
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)
st.title(" Expense Tracker")
st.caption("Personal Expense Tracking using Python + Streamlit")
create_db()
menu = st.sidebar.radio(
    "Navigation",
    [
        "Add Expense",
        "View Expenses",
        "Analytics",
        "Budget",
        "Export"
    ]
)
expenses = get_expenses()
if expenses:
    df = pd.DataFrame(
        expenses,
        columns=["ID", "Date", "Category", "Description", "Amount", "Payment"]
    )
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")
else:
    df = pd.DataFrame(
        columns=["ID", "Date", "Category", "Description", "Amount", "Payment", "Month"]
    )
if menu == "Add Expense":

    st.subheader("Add New Expense")

    with st.form("expense_form"):

        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date", datetime.date.today())
            category = st.selectbox(
                "Category",
                ["Food", "Transport", "Groceries", "Rent",
                 "Shopping", "Entertainment", "Bills", "Others"]
            )

        with col2:
            amount = st.number_input("Amount (₹)", min_value=0.0)
            payment = st.selectbox("Payment Mode", ["UPI", "Cash", "Card", "Net Banking"])

        description = st.text_input("Description")

        save_btn = st.form_submit_button("Save")

        if save_btn:
            add_expense(str(date), category, description, amount, payment)
            st.success("Expense added successfully.")
elif menu == "View Expenses":

    st.subheader("Expense History")

    if df.empty:
        st.info("No expenses added yet.")

    else:
        col1, col2 = st.columns(2)

        with col1:
            cat_filter = st.multiselect(
                "Category",
                df["Category"].unique(),
                default=df["Category"].unique()
            )

        with col2:
            pay_filter = st.multiselect(
                "Payment Mode",
                df["Payment"].unique(),
                default=df["Payment"].unique()
            )

        filtered_df = df[
            (df["Category"].isin(cat_filter)) &
            (df["Payment"].isin(pay_filter))
        ]

        st.dataframe(filtered_df.sort_values("Date", ascending=False), use_container_width=True)

        st.divider()

        st.subheader("Delete Expense")

        delete_id = st.number_input("Enter Expense ID", step=1)

        if st.button("Delete"):

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM expenses WHERE id=?", (delete_id,))
            conn.commit()
            conn.close()

            st.success("Expense deleted. Refresh page.")
elif menu == "Analytics":

    st.subheader("Expense Analytics")

    if df.empty:
        st.info("No data available.")

    else:
        total_spent = df["Amount"].sum()

        c1, c2 = st.columns(2)
        c1.metric("Total Spent", f"₹{total_spent:.0f}")
        c2.metric("Months Tracked", df["Month"].nunique())

        st.divider()

        st.subheader("Spending by Category")
        category_data = df.groupby("Category")["Amount"].sum()
        st.bar_chart(category_data)

        st.subheader("Monthly Trend")
        monthly_data = df.groupby("Month")["Amount"].sum()
        st.line_chart(monthly_data)
elif menu == "Budget":

    st.subheader("Monthly Budget")

    budget = st.number_input("Enter Monthly Budget", value=15000.0, step=500.0)

    if not df.empty:

        current_month = pd.Timestamp.today().to_period("M")
        month_data = df[df["Month"] == current_month]

        spent = month_data["Amount"].sum()
        remaining = budget - spent

        c1, c2, c3 = st.columns(3)
        c1.metric("Budget", f"₹{budget:.0f}")
        c2.metric("Spent", f"₹{spent:.0f}")
        c3.metric("Remaining", f"₹{remaining:.0f}")

        progress = min(int((spent / budget) * 100), 100)
        st.progress(progress)

        if remaining < 0:
            st.error("You crossed your budget.")
        elif remaining < budget * 0.2:
            st.warning("Budget running low.")
        else:
            st.success("Budget is under control.")

        if not month_data.empty:
            top_category = month_data.groupby("Category")["Amount"].sum().idxmax()
            st.info(f"Highest spending category: {top_category}")
elif menu == "Export":

    st.subheader("Export Expenses")

    if df.empty:
        st.info("No data to export.")

    else:
        buffer = io.BytesIO()
        df.drop(columns=["Month"]).to_excel(buffer, index=False, engine="xlsxwriter")

        st.download_button(
            "Download Excel",
            buffer.getvalue(),
            file_name="expenses.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
st.caption("Expense Tracker Project | Streamlit + SQLite | BCA Data Science")



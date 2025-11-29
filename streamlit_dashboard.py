import streamlit as st
import datetime
import pandas as pd

from features.transactions.transactions import (
    load_transactions,
    transactions,
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES
)

from features.budgets.budgets import load_budgets, budgets


st.set_page_config(layout="centered", page_title="Personal Finance Tracker Dashboard")

st.markdown("""
<style>
.reportview-container {
    max-width: 1200px;
    margin: 0 auto;
    font-family: Arial, sans-serif;
    padding: 2rem;
}
h1, h2, h3 { color: #0E1117; }
</style>
""", unsafe_allow_html=True)


def color_amount(row):
    color = 'red' if row['Type'] == 'Expense' else 'green'
    return [f'color: {color}' for _ in row.index]


def main():
    st.title("Personal Finance Tracker Dashboard")

    # Load data
    load_transactions()
    load_budgets()

    today = datetime.date.today()
    month_start = today.replace(day=1)

    # =======================
    # BALANCE SECTION
    # =======================
    st.header("Balance Overview")

    income = sum(t.amount for t in transactions if t.type == "Income" and t.date >= month_start)
    expenses = sum(t.amount for t in transactions if t.type == "Expense" and t.date >= month_start)
    balance = income - expenses

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### Income")
        st.markdown(f"## <span style='color:green;'>Rs {income/100:.2f}</span>", unsafe_allow_html=True)

    with c2:
        st.markdown("### Expenses")
        st.markdown(f"## <span style='color:red;'>Rs {expenses/100:.2f}</span>", unsafe_allow_html=True)

    with c3:
        color = "green" if balance >= 0 else "red"
        st.markdown("### Balance")
        st.markdown(f"## <span style='color:{color};'>Rs {balance/100:.2f}</span>", unsafe_allow_html=True)

    # =======================
    # BUDGET STATUS
    # =======================
    st.header("Budgets This Month")

    if budgets:
        for category, b in budgets.items():
            spent = sum(t.amount for t in transactions
                        if t.type == "Expense" and t.category == category and t.date >= month_start)

            remaining = b.amount - spent
            pct = (spent / b.amount) * 100 if b.amount > 0 else 0

            color = "green"
            if pct >= 100:
                color = "red"
            elif pct >= 70:
                color = "orange"

            st.subheader(category)
            st.markdown(
                f"Budget: **Rs {b.amount/100:.2f}** | "
                f"Spent: <span style='color:{color}; font-weight:bold;'>Rs {spent/100:.2f}</span> | "
                f"Remaining: **Rs {remaining/100:.2f}**",
                unsafe_allow_html=True
            )

            st.progress(min(pct, 100) / 100)

    else:
        st.info("No budgets set yet (add budgets via CLI).")

    # =======================
    # RECENT TRANSACTIONS
    # =======================
    st.header("Recent Transactions")

    if transactions:
        tx = sorted(transactions, key=lambda t: t.date, reverse=True)[:10]

        df = pd.DataFrame([{
            "Date": t.date.isoformat(),
            "Type": t.type,
            "Category": t.category,
            "Description": t.description,
            "Amount": t.amount / 100,
        } for t in tx])

        st.dataframe(df.style.apply(color_amount, axis=1), use_container_width=True)
    else:
        st.info("No transactions recorded yet.")


if __name__ == "__main__":
    main()





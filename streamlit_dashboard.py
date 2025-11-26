
import streamlit as st
import datetime
import pandas as pd
from collections import defaultdict

# Assume these are available or mocked for dashboard display
from features.transactions.transactions import load_transactions, transactions, Transaction, EXPENSE_CATEGORIES, INCOME_CATEGORIES
from features.budgets.budgets import load_budgets, budgets

st.set_page_config(layout="centered", page_title="Personal Finance Tracker Dashboard")

# Custom CSS for card-based design and colored progress bars
st.markdown(
    """
    <style>
    .reportview-container {
        max-width: 1200px;
        margin: 0 auto;
        font-family: Arial, sans-serif;
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    div[data-testid="stVerticalBlock"] > div:first-child {
        border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        padding: 1rem;
        background-color: #fdfdfd;
        margin-bottom: 1rem;
    }
    h1, h2, h3 {
        color: #0E1117;
    }
    .stProgress > div > div > div > div {
        background-color: #008000; /* Default green */
    }
    /* Specific colors for budget progress bars (requires more complex CSS targeting or JS injection) */
    /* For now, we'll use text-based color indicators */
    </style>
    """,
    unsafe_allow_html=True
)

def color_amount(row):
    color = 'red' if row['Type'] == 'Expense' else 'green'
    return [f'color: {color}' for _ in row.index]


def main():
    st.title("Personal Finance Tracker Dashboard")

    load_transactions()
    load_budgets()

    # --- Balance Section ---
    st.header("Balance Overview")
    with st.container():
        today = datetime.date.today()
        current_month_start = today.replace(day=1)

        current_month_income = sum(t.amount for t in transactions if t.type == "Income" and t.date >= current_month_start)
        current_month_expenses = sum(t.amount for t in transactions if t.type == "Expense" and t.date >= current_month_start)
        current_balance = current_month_income - current_month_expenses

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"### <span style='color:green;'>Income:</span>", unsafe_allow_html=True)
            st.markdown(f"## <span style='color:green;'>Rs {current_month_income / 100:.2f}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"### <span style='color:red;'>Expenses:</span>", unsafe_allow_html=True)
            st.markdown(f"## <span style='color:red;'>Rs {current_month_expenses / 100:.2f}</span>", unsafe_allow_html=True)
        with col3:
            balance_color = "green" if current_balance >= 0 else "red"
            st.markdown(f"### <span style='color:{balance_color};'>Balance:</span>", unsafe_allow_html=True)
            st.markdown(f"## <span style='color:{balance_color};'>Rs {current_balance / 100:.2f}</span>", unsafe_allow_html=True)

    # --- Budget Status Section ---
    st.header("Budget Status (This Month)")
    with st.container():
        if budgets:
            for category, budget_obj in budgets.items():
                spent = sum(t.amount for t in transactions if t.type == "Expense" and t.category == category and t.date >= current_month_start)
                remaining = budget_obj.amount - spent
                utilization_percent = (spent / budget_obj.amount) * 100 if budget_obj.amount > 0 else 0

                if utilization_percent >= 100:
                    color = "red"
                elif utilization_percent >= 70:
                    color = "orange"
                else:
                    color = "green"
                
                st.subheader(category)
                st.markdown(
                    f"Budgeted: <span style='font-weight:bold;'>Rs {budget_obj.amount / 100:.2f}</span> | "
                    f"Spent: <span style='font-weight:bold; color:{color};'>Rs {spent / 100:.2f}</span> | "
                    f"Remaining: <span style='font-weight:bold;'>Rs {remaining / 100:.2f}</span>",
                    unsafe_allow_html=True
                )
                
                progress_text_color = "white" if utilization_percent > 50 else "black"
                progress_html = f"""
                <div style="background-color: #f0f2f6; border-radius: 5px; height: 25px; width: 100%;">
                    <div style="background-color: {color}; border-radius: 5px; height: 100%; width: {min(utilization_percent, 100)}%;">
                        <span style="color: {progress_text_color}; padding-left: 5px; line-height: 25px;">{utilization_percent:.1f}%</span>
                    </div>
                </div>
                """
                st.markdown(progress_html, unsafe_allow_html=True)
        else:
            st.info("No budgets set yet. Set budgets in the CLI to see them here.")

    # --- Recent Transactions Table ---
    st.header("Recent Transactions")
    with st.container():
        if transactions:
            sorted_transactions = sorted(transactions, key=lambda t: t.date, reverse=True)[:10]
            
            tx_data = []
            for t in sorted_transactions:
                tx_data.append({
                    "Date": t.date.isoformat(),
                    "Type": t.type,
                    "Category": t.category,
                    "Description": t.description,
                    "Amount": t.amount / 100
                })
            
            df = pd.DataFrame(tx_data)
            
            # Apply color coding to the 'Amount' column
            st.dataframe(df.style.apply(color_amount, axis=1), use_container_width=True)
        else:
            st.info("No transactions recorded yet. Add some in the CLI to see them here.")


if __name__ == "__main__":
    main()

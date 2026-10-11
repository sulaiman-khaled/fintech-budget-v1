import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Financial Budget Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Financial Budget Tracker")
st.write("Track income, expenses, and monthly budget performance.")

# Initial sample transactions
initial_data = pd.DataFrame(
    [
        {
            "Date": "2026-01-05",
            "Description": "Monthly salary",
            "Category": "Income",
            "Type": "Income",
            "Amount": 5000.00
        },
        {
            "Date": "2026-01-07",
            "Description": "House rent",
            "Category": "Housing",
            "Type": "Expense",
            "Amount": 1500.00
        },
        {
            "Date": "2026-01-10",
            "Description": "Groceries",
            "Category": "Food",
            "Type": "Expense",
            "Amount": 450.00
        },
        {
            "Date": "2026-01-15",
            "Description": "Transport",
            "Category": "Transport",
            "Type": "Expense",
            "Amount": 250.00
        }
    ]
)

# Store transactions during the current Streamlit session
if "transactions" not in st.session_state:
    st.session_state.transactions = initial_data.copy()

# Sidebar: add a new transaction
st.sidebar.header("Add Transaction")

transaction_date = st.sidebar.date_input(
    "Date",
    value=date.today()
)

description = st.sidebar.text_input(
    "Description",
    placeholder="Example: Electricity bill"
)

category = st.sidebar.selectbox(
    "Category",
    [
        "Income",
        "Housing",
        "Food",
        "Transport",
        "Utilities",
        "Healthcare",
        "Education",
        "Entertainment",
        "Shopping",
        "Other"
    ]
)

transaction_type = st.sidebar.selectbox(
    "Type",
    ["Income", "Expense"]
)

amount = st.sidebar.number_input(
    "Amount",
    min_value=0.0,
    step=10.0,
    format="%.2f"
)

if st.sidebar.button("Add Transaction"):
    if description.strip() == "":
        st.sidebar.error("Please enter a description.")
    elif amount <= 0:
        st.sidebar.error("Amount must be greater than zero.")
    else:
        new_transaction = pd.DataFrame(
            [
                {
                    "Date": transaction_date.strftime("%Y-%m-%d"),
                    "Description": description,
                    "Category": category,
                    "Type": transaction_type,
                    "Amount": amount
                }
            ]
        )

        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, new_transaction],
            ignore_index=True
        )

        st.sidebar.success("Transaction added successfully.")

# Copy data for calculations
transactions = st.session_state.transactions.copy()
transactions["Date"] = pd.to_datetime(transactions["Date"])

# Calculate totals
total_income = transactions.loc[
    transactions["Type"] == "Income", "Amount"
].sum()

total_expenses = transactions.loc[
    transactions["Type"] == "Expense", "Amount"
].sum()

balance = total_income - total_expenses

# Dashboard metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Income",
        value=f"${total_income:,.2f}"
    )

with col2:
    st.metric(
        label="Total Expenses",
        value=f"${total_expenses:,.2f}"
    )

with col3:
    st.metric(
        label="Current Balance",
        value=f"${balance:,.2f}"
    )

st.divider()

# Monthly budget limit
st.subheader("Budget Settings")

monthly_budget = st.number_input(
    "Monthly expense budget",
    min_value=0.0,
    value=3000.0,
    step=100.0,
    format="%.2f"
)

budget_usage = 0.0

if monthly_budget > 0:
    budget_usage = total_expenses / monthly_budget

st.progress(
    min(budget_usage, 1.0),
    text=f"Budget used: {budget_usage * 100:.1f}%"
)

if total_expenses > monthly_budget:
    st.warning("Warning: Your expenses have exceeded the monthly budget.")
else:
    remaining = monthly_budget - total_expenses
    st.success(f"Remaining budget: ${remaining:,.2f}")

st.divider()

# Expense analysis
left_column, right_column = st.columns(2)

with left_column:
    st.subheader("Expenses by Category")

    expense_data = transactions[
        transactions["Type"] == "Expense"
    ]

    if not expense_data.empty:
        expenses_by_category = (
            expense_data
            .groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(expenses_by_category)
    else:
        st.info("No expense data available.")

with right_column:
    st.subheader("Income and Expenses")

    summary_data = pd.DataFrame(
        {
            "Amount": [
                total_income,
                total_expenses,
                balance
            ]
        },
        index=[
            "Income",
            "Expenses",
            "Balance"
        ]
    )

    st.bar_chart(summary_data)

st.divider()

# Filter transactions
st.subheader("Transaction History")

filter_type = st.selectbox(
    "Filter by transaction type",
    ["All", "Income", "Expense"]
)

if filter_type == "All":
    filtered_transactions = transactions
else:
    filtered_transactions = transactions[
        transactions["Type"] == filter_type
    ]

display_transactions = filtered_transactions.copy()
display_transactions["Date"] = display_transactions["Date"].dt.strftime(
    "%Y-%m-%d"
)

st.dataframe(
    display_transactions.sort_values(
        by="Date",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)

# Download data
csv_data = transactions.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Transactions as CSV",
    data=csv_data,
    file_name="budget_transactions.csv",
    mime="text/csv"
)

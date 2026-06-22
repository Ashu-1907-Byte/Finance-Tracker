import importlib.util
import importlib
import sys
import os

try:
    stdlib_csv_path = os.path.join(sys.base_prefix, 'Lib', 'csv.py')
    spec = importlib.util.find_spec('csv')
    if not spec or not spec.origin or os.path.normcase(spec.origin) != os.path.normcase(stdlib_csv_path):
        spec2 = importlib.util.spec_from_file_location('csv', stdlib_csv_path)
        mod = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(mod)
        sys.modules['csv'] = mod
except Exception:
    pass

import streamlit as st
from data import (
    create_table,
    save_transaction,
    get_transactions,
    get_total_expenses,
    get_total_credits,
    update_transaction,
)
import csv
print('DEBUG: csv module origin ->', importlib.util.find_spec('csv').origin)
try:
    st_csv_origin = importlib.util.find_spec('csv').origin
except Exception:
    st_csv_origin = 'unknown'

#st.write(f"CSV module origin: {st_csv_origin}")
from data_table import display_transactions
import exportcsv

if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "show_transactions" not in st.session_state:
    st.session_state.show_transactions = False

if "show_export" not in st.session_state:
    st.session_state.show_export = False

create_table()
st.header("FinTrack")
total_expenses = get_total_expenses()
total_credits = get_total_credits()
remaining_budget = total_credits - total_expenses
col1, col2 = st.columns(2)

with col1:
    st.write("Total Expenses")
    spent = st.header(total_expenses)

with col2:
    st.write("Remaining budget")
    remaining = st.header(remaining_budget)

if not st.session_state.show_form and not st.session_state.show_transactions and not st.session_state.show_export:
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Add Transaction", key="add_transaction"):
            st.session_state.show_form = True
            st.session_state.show_transactions = False
            st.session_state.show_export = False
            st.rerun()

    with col2:
        if st.button("View Transactions", key="view_transactions"):
            st.session_state.show_transactions = True
            st.session_state.show_form = False
            st.session_state.show_export = False
            st.rerun()

    with col3:
        if st.button("Export Transactions", key="export_transactions"):
            st.session_state.show_export = True
            st.session_state.show_transactions = False
            st.session_state.show_form = False
            st.rerun()

if st.session_state.show_form:
    if st.button("Go Back"):
        st.session_state.show_form = False
        st.rerun()
    with st.form("transaction_form"):
        st.subheader("Add New Transaction")

        transaction_type = st.selectbox("Transaction Type", ["Debit", "Credit"])
        category = st.selectbox("Category", ["Food", "Entertainment", "Transport", "Groceries", "Bills", "Income", "Other"])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        importance = st.selectbox("Importance", ["Important", "Moderate", "Less Important"])
        date = st.date_input("Date")
        col1, col2 = st.columns([4, 1])
        with col2:
         save = st.form_submit_button("Save Transaction")
        
        if save:
            if amount <= 0:
                st.error("Please enter an amount greater than 0.")
            else:
                save_transaction(
                    transaction_type,
                    category,
                    amount,
                    importance,
                    str(date),
                )
                st.success("Transaction successfully saved")
                st.session_state.show_form = False
                st.rerun()

if st.session_state.show_transactions:
    if st.button("Go Back", key="back_transactions"):
     st.session_state.show_transactions = False
     st.rerun()
    st.subheader("View Transactions")
    transactions = get_transactions()
    if transactions:
        st.session_state.transactions = True
        sort_choice = st.selectbox(
            "Sort by:",
            ["Default", "Type", "Category", "Amount", "Date"],
            key = "sort_choice")
        if sort_choice == "Default":
            sorted_transactions = transactions
        elif sort_choice == "Type":
            sorted_transactions = sorted(transactions, key=lambda x: x[1])
        elif sort_choice == "Category":
            sorted_transactions = sorted(transactions, key=lambda x: x[2])
        elif sort_choice == "Amount":
            sorted_transactions = sorted(transactions, key=lambda x: x[3], reverse=True)
        else:
            sorted_transactions = sorted(transactions, key=lambda x: x[4])

        st.write(f"Sorted by: {sort_choice}")
        edited_df, transaction_ids = display_transactions(sorted_transactions)

        if edited_df is not None:
            col1, col2 = st.columns([4, 1])
            with col2:
             if st.button("Save Changes", key="save_transactions"):
                updated_count = 0
                for idx, row in edited_df.iterrows():
                    original_row = sorted_transactions[idx]
                    if (
                        row["Type"] != original_row[1]
                        or row["Category"] != original_row[2]
                        or float(row["Amount"]) != float(original_row[3])
                        or str(row["Date"]) != str(original_row[4])
                    ):
                        update_transaction(
                            transaction_ids[idx],
                            row["Type"],
                            row["Category"],
                            row["Amount"],
                            str(row["Date"]),
                        )
                        updated_count += 1

                if updated_count:
                    st.success(f"Updated {updated_count} transaction(s).")
                    st.rerun()
                else:
                    st.info("No changes detected.")
    else:
        st.info("No transactions found.")
        st.session_state.transactions = False

if "csv_bytes" not in st.session_state:
    st.session_state.csv_bytes = None

if st.session_state.show_export:
    if st.button("Go Back", key="back_export"):
        st.session_state.show_export = False
        st.rerun()
    st.header("Dates for export:")
    start_date = st.date_input("Start Date", key="start_date")
    end_date = st.date_input("End Date", key="end_date")

    file_name = f"transactions_{start_date.isoformat()}_{end_date.isoformat()}.csv"


    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Export to CSV", key="export_csv"):
            if start_date > end_date:
                st.error("Start date must be before or equal to end date.")
            else:
                transactions = get_transactions()
                st.session_state.csv_bytes = exportcsv.export_transactions_to_csv(
                    transactions,
                    start_date,
                    end_date
                )
                if st.session_state.csv_bytes:
                    st.download_button(
                       label="Download CSV",
                       data=st.session_state.csv_bytes,
                       file_name=file_name,
                       mime="text/csv", 
                    )
                    st.session_state.show_export = False
                    st.success(f"Prepared {file_name} for download.")
                else:


                    left_col, center_col, right_col = st.columns([1, 2, 1])

                    if not st.session_state.csv_bytes:
                         st.error("No transactions found in the specified date range. Please adjust the dates and try again.")
                    
                    else:
                         st.success(f"Prepared {file_name} for download.")
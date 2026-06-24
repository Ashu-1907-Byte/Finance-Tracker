import streamlit as st
import pandas as pd


def display_transactions(transactions):
    if transactions:
        df_init = pd.DataFrame(transactions, columns=["id", "Type", "Category", "Amount", "Date"])
        df_init["Date"] = pd.to_datetime(df_init["Date"]).dt.date
        df = st.data_editor(
            df_init.drop(columns=["id"]),
            column_order=["Type", "Category", "Amount", "Date"],
            hide_index=True,
            use_container_width=True,
        )
        return df, df_init["id"].tolist()
    return None, []
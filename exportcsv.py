import io
import csv
from datetime import date


def _parse_date(d):
    """Try to parse a date-like string to a date object.
    Returns a date or None if parsing fails.
    """
    if isinstance(d, date):
        return d
    if d is None:
        return None
    s = str(d)
    try:
        # Expect ISO format YYYY-MM-DD
        return date.fromisoformat(s)
    except Exception:
        # Fallback: try common formats
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
            try:
                from datetime import datetime

                return datetime.strptime(s, fmt).date()
            except Exception:
                continue
    return None


def export_transactions_to_csv(transactions, start_date, end_date):
    """Filter transactions by inclusive date range and return CSV bytes.

    transactions: iterable of rows (id, transaction_type, category, amount, date)
    start_date, end_date: date objects (from Streamlit date_input)

    Returns bytes (utf-8) or None if no rows in range.
    """
    if transactions is None:
        return None

    # Normalize start/end to date objects
    if isinstance(start_date, str):
        start = _parse_date(start_date)
    else:
        start = start_date
    if isinstance(end_date, str):
        end = _parse_date(end_date)
    else:
        end = end_date

    if start is None or end is None:
        return None

    rows_in_range = []
    for row in transactions:
        # Expect row: (id, transaction_type, category, amount, date)
        try:
            row_date = _parse_date(row[4])
        except Exception:
            row_date = None
        if row_date is None:
            continue
        if start <= row_date <= end:
            rows_in_range.append(row)

    if not rows_in_range:
        return None

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Type", "Category", "Amount", "Date"]) 
    for r in rows_in_range:
        writer.writerow([r[0], r[1], r[2], r[3], r[4]])

    return output.getvalue().encode("utf-8")


    
    
   
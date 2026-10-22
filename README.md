# Expense Tracker

A simple, professional expense tracker built with Python.

- **Streamlit** for the web interface
- **SQLite** for permanent storage (file: `expenses.db`)
- **Pandas** for data handling
- **Plotly** for interactive charts

## Features

- Add, view, edit and delete expenses
- Dashboard cards: total expenses, number of transactions, average expense
- Category-wise totals, interactive pie and bar charts
- Filter by category and date range
- Input validation (amount must be greater than 0, no future dates)
- Demo data button and clear-all button
- Download expenses as a CSV file

## Project files

```
expense_tracker/
├── app.py             <- main application
├── requirements.txt   <- Python packages
├── README.md          <- this file
└── expenses.db        <- created automatically on the first run
```

## Setup and run on Windows

Open **Command Prompt** or **PowerShell**, then run these commands one by one.

1. Create a project folder and go into it:

```bat
mkdir expense_tracker
cd expense_tracker
```

Copy `app.py`, `requirements.txt` and `README.md` into this folder.

2. Create a virtual environment and activate it:

```bat
python -m venv venv
venv\Scripts\activate
```

After activation, you should see `(venv)` at the start of the command line.

3. Install the dependencies:

```bat
pip install -r requirements.txt
```

4. Run the application:

```bat
streamlit run app.py
```

5. Open the app in your browser. Streamlit usually opens it automatically. If it does not, open this address:

```
http://localhost:8501
```

To stop the app, press `Ctrl + C` in the terminal.

## How to use

1. **Load demo data** (sidebar): click the button to add 40 sample expenses. This is useful for the presentation.
2. **Dashboard tab**: view the metric cards, the pie and bar charts, category totals and the table. Use the sidebar filters to narrow the results.
3. **Add Expense tab**: enter the amount, category, date and an optional description, then click **Add Expense**.
4. **Edit / Delete tab**: select an expense, change its values and click **Save Changes**. To delete it, tick the confirmation box and click **Delete Expense**.
5. **Clear all data** (sidebar): removes every expense. Tick the confirmation box first.

## Troubleshooting

- **`python` is not recognized**: install Python from python.org and tick "Add Python to PATH" during installation. Then close and reopen the terminal.
- **`running scripts is disabled` in PowerShell**: run this once, then activate again:
  ```bat
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
- **Port already in use**: run `streamlit run app.py --server.port 8502` and open `http://localhost:8502`.
- **Want a different currency symbol?** Change `CURRENCY = "$"` near the top of `app.py`.
- **Want a fresh start?** Stop the app, delete `expenses.db`, and run the app again.

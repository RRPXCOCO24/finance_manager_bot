# Enhanced Finance Tracker

A comprehensive **command-line personal finance manager** built with Python to track income, expenses, and analyze spending patterns across multiple accounts.

---

## ✨ Features

* **Income & Expense Tracking**: Record financial transactions with categories and descriptions.
* **Multiple Account Support**: Create and manage multiple financial accounts.
* **Balance Calculation**: Real-time account balance tracking.
* **Spending Analysis**: View spending breakdown by category with percentage calculations.
* **Date Filtering**: Filter transactions and reports by date ranges.
* **Data Export**: Export transaction history to CSV files.
* **SQLite Database**: Secure and persistent data storage.
* **User-Friendly Interface**: Intuitive command-line menu system.

---

## 🚀 Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/enhanced-finance-tracker.git
cd enhanced-finance-tracker
```

Ensure you have **Python 3.7+** installed.

> ✅ The application uses only **Python standard library modules**, so no additional dependencies are required.

---

## 📌 Usage

Run the application with:

```bash
python finance_tracker.py
```

### Main Menu Options

* **Add Income**: Record income transactions with predefined or custom categories.
* **Add Expense**: Record expense transactions with predefined or custom categories.
* **View Transactions**: Display recent transactions with optional date filtering.
* **View Spending Summary**: Analyze spending by category with visual percentages.
* **Manage Accounts**: Create new accounts or switch between existing ones.
* **Export Data**: Export transaction history to CSV format.
* **Exit**: Safely close the application.

---

## 📂 Default Categories

**Income Categories:** Salary, Bonus, Investment, Gift, Other
**Expense Categories:** Food, Rent, Transport, Entertainment, Utilities, Healthcare, Other

---

## 🗄️ Database Structure

The application uses SQLite with the following tables:

* **accounts**: Stores account information (ID, name, creation date).
* **transactions**: Records all financial transactions with timestamps.
* **snapshots**: Reserved for future balance history features.

---

## 📤 Data Export

Transactions can be exported to CSV format with the following columns:

* `ID`, `Date`, `Type`, `Amount`, `Category`, `Description`

---

## 🔧 Function Examples

### 1. Core Functions

```python
current_time()
# Example output: "2023-10-15T14:30:45+0000"

format_date_display(timestamp)
# Input: "2023-10-15T14:30:45+0000"
# Output: "2023-10-15 14:30"
```

### 2. Transaction Class

```python
Transaction.display()
# Example output:
# "[5] 2023-10-15 14:30 -50.00 | Food           | Grocery shopping"
```

### 3. Database Operations

```python
# Add a new transaction
db.add_transaction(1, 50.0, "expense", "Food", "Grocery shopping")
# Returns: 5 (the new transaction ID)

# Get last 20 transactions
transactions = db.get_transactions(1, 20)

# Get transactions from October 2023
transactions = db.get_transactions(1, 100, "2023-10-01T00:00:00+0000", "2023-10-31T23:59:59+0000")

# Get balance
balance = db.get_balance(1)
# Example: 1250.75

# Get spending summary
spending = db.get_spending_by_category(1)
# Example: {"Food": 250.0, "Rent": 1000.0, "Transport": 150.0}

# Get accounts
accounts = db.get_accounts()
# Example: [Account(id=1, name="Primary Account", created_at="2023-10-15T14:30:45+0000", balance=1250.75),
#           Account(id=2, name="Savings Account", created_at="2023-10-16T09:15:30+0000", balance=5000.00)]

# Add account
account_id = db.add_account("Savings Account")
# Returns: 2

# Export transactions
success = db.export_transactions_to_csv(1, "transactions.csv")
# Returns: True if successful
```

### 4. User Interface Functions

#### FinanceManager.\_add\_income()

```text
Example flow:
1. User selects "Add Income"
2. Enters amount: 1000
3. Selects category: 1 (Salary)
4. Enters description: "Monthly salary"
5. Transaction added: "Income of 1000.00 added successfully! (ID: 6)"
```

#### FinanceManager.\_add\_expense()

```text
Example flow:
1. User selects "Add Expense"
2. Enters amount: 50
3. Selects category: 1 (Food)
4. Enters description: "Grocery shopping"
5. Transaction added: "Expense of 50.00 recorded successfully! (ID: 7)"
```

#### FinanceManager.\_view\_transactions()

```text
========== TRANSACTIONS ==========
Date filter: From 2023-10-01 To 2023-10-15
Current Balance: 1250.75

[7] 2023-10-15 14:30 -50.00 | Food           | Grocery shopping
[6] 2023-10-15 10:15 +1000.00 | Salary         | Monthly salary
[5] 2023-10-14 09:30 -25.00 | Transport      | Bus fare
```

#### FinanceManager.\_view\_spending\_summary()

```text
========== SPENDING SUMMARY ==========
Current Balance: 1250.75

Food           :   250.00 (25.0%)
Rent           :   500.00 (50.0%)
Transport      :   150.00 (15.0%)
Entertainment  :   100.00 (10.0%)
------------------------------
TOTAL         :  1000.00
```

#### FinanceManager.\_manage\_accounts()

```text
========== MANAGE ACCOUNTS ==========
Current accounts:

[1] Primary Account       | Balance: 1250.75 *
[2] Savings Account       | Balance: 5000.00

Options:
1. Switch account
2. Create new account
3. Back to main menu
```

#### FinanceManager.\_export\_data()

```text
Example flow:
1. User selects "Export Data"
2. Enters date range (optional)
3. Enters filename: "my_transactions.csv"
4. File created: "Data successfully exported to my_transactions.csv"
```

---

## ⚙️ Customization

### Adding New Categories

```python
DEFAULT_CATEGORIES = {
    "income": ["Salary", "Bonus", "Investment", "Gift", "Other", "Your New Category"],
    "expense": ["Food", "Rent", "Transport", "Entertainment", "Utilities", "Healthcare", "Other", "Your New Category"]
}
```

### Changing Database Location

```python
DB_FILE = "custom_finance.db"
```

---

## 🛡️ Error Handling

The application includes comprehensive error handling for:

* Invalid numeric inputs
* Database connection issues
* File export errors
* Invalid date formats

---

## 💾 Backup Recommendations

Regularly back up your database file (**`personal_finance.db` by default**) to prevent data loss.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a **Pull Request**.

---

## 📜 License

This project is open source and available under the **MIT License**.

---

## 🆘 Support

If you encounter any issues or have questions, please open an **issue** on the GitHub repository.

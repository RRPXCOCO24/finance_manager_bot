"""
Enhanced Finance Tracker - Income and Expense Manager
"""

import sqlite3
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
import textwrap
from enum import Enum
import csv
import os

# Constants
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
TRANSACTION_TYPES = {"income": "+", "expense": "-"}
DB_FILE = "personal_finance.db"
DEFAULT_CATEGORIES = {
    "income": ["Salary", "Bonus", "Investment", "Gift", "Other"],
    "expense": ["Food", "Rent", "Transport", "Entertainment", "Utilities", "Healthcare", "Other"]
}

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

def current_time() -> str:
    """Returns current UTC time in ISO format"""
    return datetime.now(timezone.utc).strftime(ISO_FORMAT)

def format_date_display(timestamp: str) -> str:
    """Formats ISO timestamp for display"""
    try:
        dt = datetime.strptime(timestamp, ISO_FORMAT)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return timestamp

@dataclass
class Transaction:
    id: Optional[int]
    account_id: int
    timestamp: str
    amount: float
    type: str  # 'income' or 'expense'
    category: str
    description: str

    def display(self) -> str:
        """Formatted string representation of the transaction"""
        sign = TRANSACTION_TYPES.get(self.type, "")
        formatted_date = format_date_display(self.timestamp)
        return f"[{self.id}] {formatted_date} {sign}{self.amount:.2f} | {self.category:<15} | {self.description}"

@dataclass
class Account:
    id: int
    name: str
    created_at: str
    balance: float = 0.0

    def display(self) -> str:
        """Formatted string representation of the account"""
        return f"[{self.id}] {self.name:<20} | Balance: {self.balance:.2f}"

class FinanceDatabase:
    def __init__(self, db_path: str = DB_FILE):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._initialize_database()
    
    def _initialize_database(self):
        """Creates database tables if they don't exist"""
        with self.connection:
            self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                balance REAL NOT NULL,
                transactions_data TEXT NOT NULL,
                note TEXT,
                FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE
            );
            """)
            
            # Create a default account if none exists
            if not self.connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]:
                self.connection.execute(
                    "INSERT INTO accounts (name, created_at) VALUES (?, ?)",
                    ("Primary Account", current_time())
                )

    def add_transaction(self, account_id: int, amount: float, 
                       transaction_type: str, category: str, description: str = "") -> int:
        """Adds a new transaction to the database"""
        if transaction_type not in [t.value for t in TransactionType]:
            raise ValueError("Transaction type must be 'income' or 'expense'")
        
        with self.connection:
            cursor = self.connection.execute(
                """
                INSERT INTO transactions 
                (account_id, timestamp, amount, type, category, description) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (account_id, current_time(), amount, transaction_type, category, description)
            )
            return cursor.lastrowid

    def get_transactions(self, account_id: int, limit: int = 20, 
                        start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Transaction]:
        """Retrieves transactions for an account with optional date filtering"""
        query = """
            SELECT * FROM transactions 
            WHERE account_id = ? 
        """
        params = [account_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
            
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.connection.execute(query, params)
        return [
            Transaction(row["id"], row["account_id"], row["timestamp"], 
                       row["amount"], row["type"], row["category"], row["description"])
            for row in cursor.fetchall()
        ]

    def get_balance(self, account_id: int) -> float:
        """Calculates current account balance"""
        cursor = self.connection.execute(
            """
            SELECT 
                SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expense
            FROM transactions 
            WHERE account_id = ?
            """,
            (account_id,)
        )
        result = cursor.fetchone()
        return (result["income"] or 0) - (result["expense"] or 0)

    def get_spending_by_category(self, account_id: int, 
                                start_date: Optional[str] = None, 
                                end_date: Optional[str] = None) -> Dict[str, float]:
        """Returns expense totals grouped by category with optional date filtering"""
        query = """
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE account_id = ? AND type = 'expense' 
        """
        params = [account_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
            
        query += " GROUP BY category"
        
        cursor = self.connection.execute(query, params)
        return {row["category"]: row["total"] for row in cursor.fetchall()}

    def get_accounts(self) -> List[Account]:
        """Retrieves all accounts with their current balances"""
        cursor = self.connection.execute("SELECT * FROM accounts ORDER BY id")
        accounts = []
        for row in cursor.fetchall():
            balance = self.get_balance(row["id"])
            accounts.append(Account(row["id"], row["name"], row["created_at"], balance))
        return accounts

    def add_account(self, name: str) -> int:
        """Adds a new account"""
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO accounts (name, created_at) VALUES (?, ?)",
                (name, current_time())
            )
            return cursor.lastrowid

    def export_transactions_to_csv(self, account_id: int, filename: str,
                                  start_date: Optional[str] = None, 
                                  end_date: Optional[str] = None) -> bool:
        """Exports transactions to a CSV file"""
        transactions = self.get_transactions(account_id, 1000000, start_date, end_date)  # Large limit to get all
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['id', 'date', 'type', 'amount', 'category', 'description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for tx in transactions:
                    writer.writerow({
                        'id': tx.id,
                        'date': format_date_display(tx.timestamp),
                        'type': tx.type,
                        'amount': tx.amount,
                        'category': tx.category,
                        'description': tx.description
                    })
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def close(self):
        """Closes the database connection"""
        self.connection.close()

class FinanceManager:
    """User interface for managing finances"""
    
    def __init__(self):
        self.db = FinanceDatabase()
        self.current_account = 1  # Default account ID
    
    def display_menu(self):
        """Main menu interface"""
        while True:
            self._clear_screen()
            accounts = self.db.get_accounts()
            current_acc = next((acc for acc in accounts if acc.id == self.current_account), None)
            
            print("\n" + "="*10 + " PERSONAL FINANCE MANAGER " + "="*10)
            if current_acc:
                print(f"Current Account: {current_acc.name} | Balance: {current_acc.balance:.2f}")
            print("\nMain Menu:")
            print("1. Add Income")
            print("2. Add Expense")
            print("3. View Transactions")
            print("4. View Spending Summary")
            print("5. Manage Accounts")
            print("6. Export Data")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                self._add_income()
            elif choice == "2":
                self._add_expense()
            elif choice == "3":
                self._view_transactions()
            elif choice == "4":
                self._view_spending_summary()
            elif choice == "5":
                self._manage_accounts()
            elif choice == "6":
                self._export_data()
            elif choice == "7":
                print("\nExiting the finance manager. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("Press Enter to continue...")

    def _add_income(self):
        """Add an income transaction"""
        self._clear_screen()
        print("\n" + "="*10 + " ADD INCOME " + "="*10)
        print(f"Current Balance: {self.db.get_balance(self.current_account):.2f}\n")
        
        try:
            amount = float(input("Amount: "))
            if amount <= 0:
                print("\nAmount must be positive.")
                input("Press Enter to continue...")
                return
                
            print("\nCommon categories:")
            for i, category in enumerate(DEFAULT_CATEGORIES["income"]):
                print(f"{i+1}. {category}")
                
            category_choice = input("\nChoose a category (1-5) or enter a new one: ").strip()
            
            if category_choice.isdigit() and 1 <= int(category_choice) <= len(DEFAULT_CATEGORIES["income"]):
                category = DEFAULT_CATEGORIES["income"][int(category_choice)-1]
            else:
                category = category_choice if category_choice else "Other"
                
            description = input("Description (optional): ").strip()
            
            transaction_id = self.db.add_transaction(
                self.current_account, amount, "income", category, description
            )
            
            print(f"\nIncome of {amount:.2f} added successfully! (ID: {transaction_id})")
            print(f"New Balance: {self.db.get_balance(self.current_account):.2f}")
        except ValueError:
            print("\nInvalid amount. Please enter a valid number.")
        except Exception as e:
            print(f"\nError adding transaction: {e}")
        
        input("\nPress Enter to return to main menu...")

    def _add_expense(self):
        """Add an expense transaction"""
        self._clear_screen()
        print("\n" + "="*10 + " ADD EXPENSE " + "="*10)
        print(f"Current Balance: {self.db.get_balance(self.current_account):.2f}\n")
        
        try:
            amount = float(input("Amount: "))
            if amount <= 0:
                print("\nAmount must be positive.")
                input("Press Enter to continue...")
                return
                
            print("\nCommon categories:")
            for i, category in enumerate(DEFAULT_CATEGORIES["expense"]):
                print(f"{i+1}. {category}")
                
            category_choice = input("\nChoose a category (1-7) or enter a new one: ").strip()
            
            if category_choice.isdigit() and 1 <= int(category_choice) <= len(DEFAULT_CATEGORIES["expense"]):
                category = DEFAULT_CATEGORIES["expense"][int(category_choice)-1]
            else:
                category = category_choice if category_choice else "Other"
                
            description = input("Description (optional): ").strip()
            
            transaction_id = self.db.add_transaction(
                self.current_account, amount, "expense", category, description
            )
            
            print(f"\nExpense of {amount:.2f} recorded successfully! (ID: {transaction_id})")
            print(f"New Balance: {self.db.get_balance(self.current_account):.2f}")
        except ValueError:
            print("\nInvalid amount. Please enter a valid number.")
        except Exception as e:
            print(f"\nError adding transaction: {e}")
        
        input("\nPress Enter to return to main menu...")

    def _get_date_range(self) -> Tuple[Optional[str], Optional[str]]:
        """Get date range from user for filtering"""
        print("\nFilter by date range (leave blank for no filter)")
        start_date = input("Start date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD): ").strip()
        
        # Convert to proper ISO format if provided
        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime(ISO_FORMAT)
            if end_date:
                # Set end date to end of day
                end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(
                    hour=23, minute=59, second=59
                ).strftime(ISO_FORMAT)
        except ValueError:
            print("Invalid date format. Using no filter.")
            return None, None
            
        return start_date, end_date

    def _view_transactions(self, limit: int = 50):
        """Display recent transactions with date filtering"""
        start_date, end_date = self._get_date_range()
        transactions = self.db.get_transactions(self.current_account, limit, start_date, end_date)
        
        self._clear_screen()
        print("\n" + "="*10 + " TRANSACTIONS " + "="*10)
        
        if start_date or end_date:
            print("Date filter: ", end="")
            if start_date:
                print(f"From {format_date_display(start_date)} ", end="")
            if end_date:
                print(f"To {format_date_display(end_date)}", end="")
            print()
                
        print(f"Current Balance: {self.db.get_balance(self.current_account):.2f}\n")
        
        if not transactions:
            print("No transactions found.")
        else:
            for tx in transactions:
                print(tx.display())
        
        input("\nPress Enter to return to main menu...")

    def _view_spending_summary(self):
        """Show spending breakdown by category with date filtering"""
        start_date, end_date = self._get_date_range()
        spending = self.db.get_spending_by_category(self.current_account, start_date, end_date)
        
        self._clear_screen()
        print("\n" + "="*10 + " SPENDING SUMMARY " + "="*10)
        
        if start_date or end_date:
            print("Date filter: ", end="")
            if start_date:
                print(f"From {format_date_display(start_date)} ", end="")
            if end_date:
                print(f"To {format_date_display(end_date)}", end="")
            print()
                
        print(f"Current Balance: {self.db.get_balance(self.current_account):.2f}\n")
        
        if not spending:
            print("No expenses recorded yet.")
        else:
            total = sum(spending.values())
            for category, amount in sorted(spending.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total) * 100 if total > 0 else 0
                print(f"{category:<15}: {amount:8.2f} ({percentage:.1f}%)")
            print("-" * 30)
            print(f"{'TOTAL':<15}: {total:8.2f}")
        
        input("\nPress Enter to return to main menu...")

    def _manage_accounts(self):
        """Manage multiple accounts"""
        while True:
            self._clear_screen()
            accounts = self.db.get_accounts()
            
            print("\n" + "="*10 + " MANAGE ACCOUNTS " + "="*10)
            print("Current accounts:\n")
            
            for acc in accounts:
                marker = " *" if acc.id == self.current_account else ""
                print(f"{acc.display()}{marker}")
                
            print("\nOptions:")
            print("1. Switch account")
            print("2. Create new account")
            print("3. Back to main menu")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                try:
                    acc_id = int(input("Enter account ID to switch to: "))
                    if any(acc.id == acc_id for acc in accounts):
                        self.current_account = acc_id
                        print(f"Switched to account ID {acc_id}")
                    else:
                        print("Invalid account ID.")
                    input("Press Enter to continue...")
                except ValueError:
                    print("Invalid account ID.")
                    input("Press Enter to continue...")
                    
            elif choice == "2":
                name = input("Enter new account name: ").strip()
                if name:
                    new_id = self.db.add_account(name)
                    print(f"Created new account: {name} (ID: {new_id})")
                    # Refresh accounts list
                    accounts = self.db.get_accounts()
                else:
                    print("Account name cannot be empty.")
                input("Press Enter to continue...")
                
            elif choice == "3":
                break
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")

    def _export_data(self):
        """Export transactions to CSV"""
        self._clear_screen()
        print("\n" + "="*10 + " EXPORT DATA " + "="*10)
        
        start_date, end_date = self._get_date_range()
        filename = input("Enter filename for export (e.g., transactions.csv): ").strip()
        
        if not filename:
            print("Filename is required.")
            input("Press Enter to continue...")
            return
            
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        success = self.db.export_transactions_to_csv(self.current_account, filename, start_date, end_date)
        
        if success:
            print(f"Data successfully exported to {filename}")
            print(f"File location: {os.path.abspath(filename)}")
        else:
            print("Export failed.")
            
        input("Press Enter to continue...")

    @staticmethod
    def _clear_screen():
        """Clear the console screen (cross-platform)"""
        # For Windows
        if os.name == 'nt':
            os.system('cls')
        # For Unix-based systems
        else:
            os.system('clear')

def main():
    """Main entry point for the finance manager"""
    manager = FinanceManager()
    try:
        manager.display_menu()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        manager.db.close()

if __name__ == "__main__":
    main()
    
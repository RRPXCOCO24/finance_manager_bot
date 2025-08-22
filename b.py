"""
Enhanced Finance Tracker - Income and Expense Manager
"""

import sqlite3
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import textwrap
from enum import Enum

# Constants
ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
TRANSACTION_TYPES = {"income": "+", "expense": "-"}
DB_FILE = "personal_finance.db"

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

def current_time() -> str:
    """Returns current UTC time in ISO format"""
    return datetime.now(timezone.utc).strftime(ISO_FORMAT)

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
        return f"[{self.id}] {self.timestamp[:10]} {sign}{self.amount:.2f} | {self.category:<15} | {self.description}"

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

    def get_transactions(self, account_id: int, limit: int = 20) -> List[Transaction]:
        """Retrieves recent transactions for an account"""
        cursor = self.connection.execute(
            """
            SELECT * FROM transactions 
            WHERE account_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (account_id, limit)
        )
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

    def get_spending_by_category(self, account_id: int) -> Dict[str, float]:
        """Returns expense totals grouped by category"""
        cursor = self.connection.execute(
            """
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE account_id = ? AND type = 'expense' 
            GROUP BY category
            """,
            (account_id,)
        )
        return {row["category"]: row["total"] for row in cursor.fetchall()}

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
            print("\n" + "="*10 + " PERSONAL FINANCE MANAGER " + "="*10)
            print(f"Current Balance: {self.db.get_balance(self.current_account):.2f}")
            print("\nMain Menu:")
            print("1. Add Income")
            print("2. Add Expense")
            print("3. View Transactions")
            print("4. View Spending Summary")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self._add_income()
            elif choice == "2":
                self._add_expense()
            elif choice == "3":
                self._view_transactions()
            elif choice == "4":
                self._view_spending_summary()
            elif choice == "5":
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
            category = input("Category (e.g., Salary, Bonus, Gift): ").strip()
            description = input("Description (optional): ").strip()
            
            transaction_id = self.db.add_transaction(
                self.current_account, amount, "income", category, description
            )
            
            print(f"\nIncome of {amount:.2f} added successfully! (ID: {transaction_id})")
            print(f"New Balance: {self.db.get_balance(self.current_account):.2f}")
        except ValueError:
            print("\nInvalid amount. Please enter a valid number.")
        
        input("\nPress Enter to return to main menu...")

    def _add_expense(self):
        """Add an expense transaction"""
        self._clear_screen()
        print("\n" + "="*10 + " ADD EXPENSE " + "="*10)
        print(f"Current Balance: {self.db.get_balance(self.current_account):.2f}\n")
        
        try:
            amount = float(input("Amount: "))
            category = input("Category (e.g., Food, Rent, Transport): ").strip()
            description = input("Description (optional): ").strip()
            
            transaction_id = self.db.add_transaction(
                self.current_account, amount, "expense", category, description
            )
            
            print(f"\nExpense of {amount:.2f} recorded successfully! (ID: {transaction_id})")
            print(f"New Balance: {self.db.get_balance(self.current_account):.2f}")
        except ValueError:
            print("\nInvalid amount. Please enter a valid number.")
        
        input("\nPress Enter to return to main menu...")

    def _view_transactions(self, limit: int = 20):
        """Display recent transactions"""
        transactions = self.db.get_transactions(self.current_account, limit)
        
        self._clear_screen()
        print("\n" + "="*10 + " RECENT TRANSACTIONS " + "="*10)
        print(f"Current Balance: {self.db.get_balance(self.current_account):.2f}\n")
        
        if not transactions:
            print("No transactions found.")
        else:
            for tx in transactions:
                print(tx.display())
        
        input("\nPress Enter to return to main menu...")

    def _view_spending_summary(self):
        """Show spending breakdown by category"""
        spending = self.db.get_spending_by_category(self.current_account)
        
        self._clear_screen()
        print("\n" + "="*10 + " SPENDING SUMMARY " + "="*10)
        print(f"Current Balance: {self.db.get_balance(self.current_account):.2f}\n")
        
        if not spending:
            print("No expenses recorded yet.")
        else:
            for category, total in spending.items():
                print(f"{category:<15}: {total:.2f}")
        
        input("\nPress Enter to return to main menu...")

    @staticmethod
    def _clear_screen():
        """Clear the console screen (cross-platform)"""
        print("\n" * 100)  # Simple solution that works in most environments

def main():
    """Main entry point for the finance manager"""
    manager = FinanceManager()
    try:
        manager.display_menu()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    finally:
        manager.db.close()

if __name__ == "__main__":
    main()

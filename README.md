
# 📊 Enhanced Finance Tracker

A **command-line personal finance manager** built in **Python** using **SQLite**.  
It helps you keep track of your **income and expenses**, view **transaction history**, and analyze your **spending habits** by category — all in a simple terminal interface.

---

## 🌟 Features
✅ Add **Income** transactions (Salary, Bonus, Gift, etc.)  
✅ Add **Expense** transactions (Food, Rent, Transport, etc.)  
✅ View **Current Balance** at any time  
✅ View **Recent Transactions** (formatted and organized)  
✅ Get a **Spending Summary** (grouped by categories)  
✅ Data stored safely in **SQLite database (`personal_finance.db`)**  
✅ Runs **offline** — no internet needed  
✅ Clean and simple **menu-driven interface**  

---

## 🗂 Project Structure
```
enhanced-finance-tracker/
│-- finance_tracker.py       # Main Python program
│-- personal_finance.db      # SQLite database file (auto-created)
│-- README.md                # Project documentation
```

---

## ⚙️ How It Works
1. **Database Setup**
   - Creates tables:
     - `accounts` → stores accounts (default: Primary Account).
     - `transactions` → stores each income/expense.
     - `snapshots` → stores balance snapshots (future use).
   - Uses SQLite (lightweight database, works without setup).

2. **Transactions**
   - Each transaction includes:
     - `amount` → how much money  
     - `type` → income or expense  
     - `category` → e.g., Salary, Food, Rent  
     - `description` → optional notes  
     - `timestamp` → when it was added  

3. **Balance Calculation**
   - **Balance = Total Income – Total Expenses**

4. **Menu Options**
   ```
   1. Add Income
   2. Add Expense
   3. View Transactions
   4. View Spending Summary
   5. Exit
   ```

---

## 🚀 Installation & Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/enhanced-finance-tracker.git
   cd enhanced-finance-tracker
   ```

2. **Run the program**
   ```bash
   python finance_tracker.py
   ```

3. The database file (`personal_finance.db`) will be created automatically when you run it for the first time.

---

## 💻 Usage Example

**Main Menu**
```
========== PERSONAL FINANCE MANAGER ==========
Current Balance: 1200.00

Main Menu:
1. Add Income
2. Add Expense
3. View Transactions
4. View Spending Summary
5. Exit
```

**Adding Income**
```
========== ADD INCOME ==========
Current Balance: 1200.00

Amount: 1000
Category: Salary
Description: August Salary

Income of 1000.00 added successfully!
New Balance: 2200.00
```

**Viewing Transactions**
```
========== RECENT TRANSACTIONS ==========
Current Balance: 2200.00

[1] 2025-08-15 +1000.00 | Salary          | August Salary
[2] 2025-08-16 -200.00  | Food            | Dinner with friends
```

**Spending Summary**
```
========== SPENDING SUMMARY ==========
Current Balance: 2000.00

Food            : 200.00
Rent            : 800.00
Transport       : 120.00
```

---

## 🛠 Technologies Used
- **Python 3**
- **SQLite3** (database)
- **Dataclasses & Enums** (for structured code)
- **Command-line interface**

---

## 📌 Future Improvements
🔹 Multiple accounts support (e.g., Cash, Bank, Wallet)  
🔹 Export reports to **CSV/PDF**  
🔹 Monthly/Yearly summaries  
🔹 Simple **GUI (Graphical User Interface)** version  
🔹 Budgeting & Alerts  

---

## 🤝 Contributing
Contributions are welcome! 🎉  
To contribute:
1. Fork the repo  
2. Create a new branch (`feature-xyz`)  
3. Commit your changes  
4. Open a Pull Request  

---

## 📜 License
This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## 👨‍💻 Author
Developed by **[Your Name]** ✨  
If you like this project, don’t forget to ⭐ star the repo!  

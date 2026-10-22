import os
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

FILE = "expenses.csv"
COLUMNS = ["date", "category", "description", "amount"]
BUDGETS = {"Food": 8000, "Transport": 3000, "Entertainment": 2000}


def load_data():
    if os.path.exists(FILE):
        df = pd.read_csv(FILE, parse_dates=["date"])
    else:
        df = pd.DataFrame(columns=COLUMNS)
        df["date"] = pd.to_datetime(df["date"])
    return df


def save_data(df):
    df.to_csv(FILE, index=False)


def add_expense(category, description, amount, date=None):
    df = load_data()
    date = pd.to_datetime(date) if date else pd.Timestamp.today().normalize()
    new_row = pd.DataFrame([{
        "date": date,
        "category": category.strip().title(),
        "description": description,
        "amount": float(amount),
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    print(f"Added: {category} - {amount}")


def view_expenses(category=None, month=None):
    df = load_data()
    if category:
        df = df[df["category"] == category.title()]
    if month:
        df = df[df["date"].dt.strftime("%Y-%m") == month]
    print(df.sort_values("date", ascending=False).to_string(index=False))
    return df


def summary():
    df = load_data()
    if df.empty:
        print("No data yet.")
        return

    df["month"] = df["date"].dt.to_period("M")

    print("\nTotal spent:", round(df["amount"].sum(), 2))
    print("\nBy category:\n", df.groupby("category")["amount"].sum().sort_values(ascending=False))
    print("\nBy month:\n", df.groupby("month")["amount"].sum())
    print("\nAverage expense:", round(df["amount"].mean(), 2))
    print("Largest expense:\n", df.loc[df["amount"].idxmax()])


def plot_expenses():
    df = load_data()
    if df.empty:
        print("No data yet.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    by_cat = df.groupby("category")["amount"].sum()
    axes[0].pie(by_cat, labels=by_cat.index, autopct="%1.1f%%")
    axes[0].set_title("Spending by Category")

    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum()
    axes[1].bar(monthly.index, monthly.values)
    axes[1].set_title("Monthly Spending")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Amount")
    plt.setp(axes[1].get_xticklabels(), rotation=45)

    plt.tight_layout()
    plt.show()


def check_budgets(month=None):
    df = load_data()
    month = month or datetime.today().strftime("%Y-%m")
    df = df[df["date"].dt.strftime("%Y-%m") == month]
    spent = df.groupby("category")["amount"].sum()

    for cat, limit in BUDGETS.items():
        used = spent.get(cat, 0)
        status = "OVER BUDGET" if used > limit else "OK"
        print(f"{cat}: {used:.0f}/{limit} -> {status}")


def main():
    while True:
        print("\n1. Add expense  2. View  3. Summary  4. Plot  5. Budget check  6. Quit")
        choice = input("Choose: ").strip()

        if choice == "1":
            cat = input("Category: ")
            desc = input("Description: ")
            amt = input("Amount: ")
            date = input("Date (YYYY-MM-DD, blank for today): ") or None
            try:
                add_expense(cat, desc, amt, date)
            except ValueError:
                print("Invalid amount or date.")
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            summary()
        elif choice == "4":
            plot_expenses()
        elif choice == "5":
            check_budgets()
        elif choice == "6":
            break


if __name__ == "__main__":
    main()
    
import questionary
import csv
import datetime
import json
import os
import shutil
import glob
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from features.budgets.budgets import (
    load_budgets as load_budgets_analytics,
    budgets as budgets_analytics,
)
from features.smart_assistant.smart_assistant import generate_smart_recommendations
from features.transactions.transactions import (
    Transaction,
    save_transactions,
    TRANSACTIONS_FILE,
)
from features.budgets.budgets import BUDGET_CATEGORIES

console = Console()


def export_transactions_csv():
    load_transactions()

    if not transactions:
        console.print(
            Panel(
                Text("No transactions to export.", style="bold yellow"),
                border_style="yellow",
            )
        )
        return

    file_name = questionary.text(
        "Enter CSV file name (e.g., transactions.csv):", qmark="[?]"
    ).ask()
    if not file_name:
        console.print("[bold red]File name cannot be empty.[/bold red]")
        return

    try:
        with open(file_name, "w", newline="") as csvfile:
            fieldnames = ["Date", "Type", "Category", "Description", "Amount"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for t in transactions:
                writer.writerow(
                    {
                        "Date": t.date.isoformat(),
                        "Type": t.type,
                        "Category": t.category,
                        "Description": t.description,
                        "Amount": t.amount / 100,
                    }
                )
        console.print(
            Panel(
                Text(
                    f"Transactions exported successfully to [bold green]{file_name}[/bold green]",
                    justify="center",
                    style="bold green",
                ),
                border_style="green",
            )
        )
    except Exception as e:
        console.print(
            Panel(
                Text(
                    f"Error exporting transactions: [bold red]{e}[/bold red]",
                    justify="center",
                    style="bold red",
                ),
                border_style="red",
            )
        )


def export_transactions_json():
    load_transactions()

    if not transactions:
        console.print(
            Panel(
                Text("No transactions to export.", style="bold yellow"),
                border_style="yellow",
            )
        )
        return

    file_name = questionary.text(
        "Enter JSON file name (e.g., transactions.json):", qmark="[?]"
    ).ask()
    if not file_name:
        console.print("[bold red]File name cannot be empty.[/bold red]")
        return

    try:
        transactions_data = [t.to_dict() for t in transactions]
        with open(file_name, "w") as jsonfile:
            json.dump(transactions_data, jsonfile, indent=4)
        console.print(
            Panel(
                Text(
                    f"Transactions exported successfully to [bold green]{file_name}[/bold green]",
                    justify="center",
                    style="bold green",
                ),
                border_style="green",
            )
        )
    except Exception as e:
        console.print(
            Panel(
                Text(
                    f"Error exporting transactions: [bold red]{e}[/bold red]",
                    justify="center",
                    style="bold red",
                ),
                border_style="red",
            )
        )


def export_monthly_report():
    load_transactions()
    load_budgets_analytics()

    report = {}
    today = datetime.date.today()
    current_month_start = today.replace(day=1)

    report["transactions_current_month"] = [
        t.to_dict() for t in transactions if t.date >= current_month_start
    ]

    budget_summary = {}
    for category, budget_obj in budgets_analytics.items():
        spent = sum(
            t.amount
            for t in transactions
            if t.type == "Expense"
            and t.category == category
            and t.date >= current_month_start
        )
        budget_summary[category] = {
            "budgeted": budget_obj.amount / 100,
            "spent": spent / 100,
            "remaining": (budget_obj.amount - spent) / 100,
        }
    report["budget_summary"] = budget_summary

    total_income_cm = sum(
        t.amount
        for t in transactions
        if t.type == "Income" and t.date >= current_month_start
    )
    total_expenses_cm = sum(
        t.amount
        for t in transactions
        if t.type == "Expense" and t.date >= current_month_start
    )
    monthly_savings_cm = total_income_cm - total_expenses_cm

    report["analytics_summary"] = {
        "total_income": total_income_cm / 100,
        "total_expenses": total_expenses_cm / 100,
        "monthly_savings": monthly_savings_cm / 100,
    }

    file_name = questionary.text(
        "Enter JSON file name for monthly report (e.g., monthly_report.json):",
        qmark="[?]",
    ).ask()
    if not file_name:
        console.print("[bold red]File name cannot be empty.[/bold red]")
        return

    try:
        with open(file_name, "w") as jsonfile:
            json.dump(report, jsonfile, indent=4)
        console.print(
            Panel(
                Text(
                    f"Monthly report exported successfully to [bold green]{file_name}[/bold green]",
                    justify="center",
                    style="bold green",
                ),
                border_style="green",
            )
        )
    except Exception as e:
        console.print(
            Panel(
                Text(
                    f"Error exporting monthly report: [bold red]{e}[/bold red]",
                    justify="center",
                    style="bold red",
                ),
                border_style="red",
            )
        )


def import_transactions_csv():
    file_name = questionary.text(
        "Enter CSV file name to import (e.g., transactions.csv):", qmark="[?]"
    ).ask()
    if not file_name:
        console.print("[bold red]File name cannot be empty.[/bold red]")
        return

    try:
        new_transactions = []
        with open(file_name, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not all(
                    k in row
                    for k in ["Date", "Type", "Category", "Description", "Amount"]
                ):
                    console.print(
                        f"[bold red]Skipping row due to missing columns: {row}[/bold red]"
                    )
                    continue
                try:
                    date = datetime.datetime.fromisoformat(row["Date"]).date()
                    amount = int(float(row["Amount"]) * 100)
                    transaction_type = row["Type"]
                    category = row["Category"]
                    description = row["Description"]
                    new_transactions.append(
                        Transaction(
                            date, transaction_type, category, description, amount
                        )
                    )
                except ValueError as ve:
                    console.print(
                        f"[bold red]Skipping row due to data conversion error: {row} - {ve}[/bold red]"
                    )
                    continue

        if not new_transactions:
            console.print(
                Panel(
                    Text(
                        "No valid transactions found in CSV to import.",
                        style="bold yellow",
                    ),
                    border_style="yellow",
                )
            )
            return

        console.print(
            f"\n[bold blue]{len(new_transactions)} new transactions found in {file_name}.[/bold blue]"
        )
        confirm = questionary.confirm(
            "Do you want to import these transactions?"
        ).ask()

        if confirm:
            load_transactions()
            initial_count = len(transactions)
            for new_t in new_transactions:
                duplicate = any(
                    (
                        new_t.date == t.date
                        and new_t.type == t.type
                        and new_t.category == t.category
                        and new_t.amount == t.amount
                    )
                    for t in transactions
                )
                if not duplicate:
                    transactions.append(new_t)

            save_transactions()
            imported_count = len(transactions) - initial_count

            console.print(
                Panel(
                    Text(
                        f"Successfully imported [bold green]{imported_count}[/bold green] new transactions.",
                        justify="center",
                        style="bold green",
                    ),
                    border_style="green",
                )
            )
        else:
            console.print("[bold yellow]Import cancelled.[/bold yellow]")

    except FileNotFoundError:
        console.print(
            Panel(
                Text(
                    f"[bold red]File not found: {file_name}[/bold red]",
                    justify="center",
                    style="bold red",
                ),
                border_style="red",
            )
        )
    except Exception as e:
        console.print(
            Panel(
                Text(
                    f"Error importing transactions: [bold red]{e}[/bold red]",
                    justify="center",
                    style="bold red",
                ),
                border_style="red",
            )
        )


def backup_data():
    console.print(
        Panel(
            Text("Backing up data...", justify="center", style="bold blue"),
            border_style="blue",
        )
    )

    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)

    try:
        temp_source = os.path.join(backup_dir, f"temp_{timestamp}")
        os.makedirs(temp_source, exist_ok=True)

        shutil.copy("database/transactions.txt", temp_source)
        shutil.copy("database/budgets.txt", temp_source)
        if os.path.exists("database/goals.txt"):
            shutil.copy("database/goals.txt", temp_source)

        shutil.make_archive(backup_path, "zip", temp_source)
        shutil.rmtree(temp_source)

        console.print(
            Panel(
                Text(
                    f"Backup created successfully: [bold green]{backup_path}.zip[/bold green]",
                    justify="center",
                    style="bold green",
                ),
                border_style="green",
            )
        )

        all_backups = sorted(
            glob.glob(os.path.join(backup_dir, "backup_*.zip")),
            key=os.path.getmtime,
            reverse=True,
        )

        if len(all_backups) > 10:
            for old in all_backups[10:]:
                os.remove(old)
                console.print(f"[yellow]Removed old backup: {old}[/yellow]")

    except Exception as e:
        console.print(
            Panel(
                Text(
                    f"Error creating backup: [bold red]{e}[/bold red]",
                    justify="center",
                    style="bold red",
                ),
                border_style="red",
            )
        )
        pass


def data_validation():
    console.print(
        Panel(
            Text("Performing Data Validation...", justify="center", style="bold blue"),
            border_style="blue",
        )
    )

    issues = []

    # Validate Transactions
    load_transactions()
    for i, t in enumerate(transactions):
        if not all([t.date, t.type, t.category, t.description, t.amount is not None]):
            issues.append(f"Transaction {i+1}: Missing fields")

        if not isinstance(t.amount, int):
            issues.append(f"Transaction {i+1}: Amount must be int")

        if t.type == "Expense" and t.category not in BUDGET_CATEGORIES:
            issues.append(f"Transaction {i+1}: Unknown expense category {t.category}")

    if issues:
        console.print(
            Panel(
                Text(
                    "Data Validation Issues Found:",
                    justify="center",
                    style="bold red",
                ),
                border_style="red",
            )
        )
        for issue in issues:
            console.print(f"- {issue}")
    else:
        console.print(
            Panel(
                Text(
                    "Data validation complete: No issues found!",
                    justify="center",
                    style="bold green",
                ),
                border_style="green",
            )
        )


def display_data_management_menu():
    while True:
        choice = questionary.select(
            "Data Management",
            choices=[
                "Export Transactions (CSV)",
                "Export Transactions (JSON)",
                "Export Monthly Report",
                "Import Transactions (CSV)",
                "Backup Data",
                "Data Validation",
                "Back to Main Menu",
            ],
        ).ask()

        if choice == "Export Transactions (CSV)":
            export_transactions_csv()
        elif choice == "Export Transactions (JSON)":
            export_transactions_json()
        elif choice == "Export Monthly Report":
            export_monthly_report()
        elif choice == "Import Transactions (CSV)":
            import_transactions_csv()
        elif choice == "Backup Data":
            backup_data()
        elif choice == "Data Validation":
            data_validation()
        elif choice == "Back to Main Menu":
            break


import datetime
import json
import questionary
from rich.console import Console
from rich.table import Table
from rich.progress_bar import ProgressBar

# In-memory database for budgets
budgets = {}
BUDGETS_FILE = "database/budgets.txt"

# Budget categories
BUDGET_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]

class Budget:
    def __init__(self, category, amount):
        self.category = category
        self.amount = amount  # Stored as an integer (paisa/cents)

    def to_dict(self):
        return {
            "category": self.category,
            "amount": self.amount
        }

def load_budgets():
    """Loads budgets from the file."""
    global budgets
    try:
        with open(BUDGETS_FILE, "r") as f:
            data = json.load(f)
            budgets = {b["category"]: Budget(b["category"], b["amount"]) for b in data}
    except (FileNotFoundError, json.JSONDecodeError):
        budgets = {}

def save_budgets():
    """Saves budgets to the file."""
    with open(BUDGETS_FILE, "w") as f:
        json.dump([b.to_dict() for b in budgets.values()], f, indent=4)

def set_budget():
    """Sets a monthly budget for a category."""
    load_budgets()
    console = Console()
    try:
        category = questionary.select(
            "Select a category to budget:",
            choices=BUDGET_CATEGORIES,
            qmark="[?]"
        ).ask()
        if category is None: return

        amount_str = questionary.text(
            f"Enter the monthly budget for {category}:",
            validate=lambda text: text.isdigit() and float(text) > 0,
            qmark="[?]"
        ).ask()
        if amount_str is None: return

        amount = int(float(amount_str) * 100)

        budgets[category] = Budget(category, amount)
        save_budgets()
        console.print(f"[bold green]Budget for {category} set to {amount / 100:.2f}[/bold green]")
    except (ValueError, TypeError):
        console.print("[bold red]Invalid input. Please try again.[/bold red]")

from features.transactions.transactions import transactions, load_transactions
from rich.text import Text

def view_budgets():
    """Views budget vs actual spending."""
    load_budgets()
    load_transactions()
    console = Console()

    if not budgets:
        console.print("[bold yellow]No budgets set. Please set a budget first.[/bold yellow]")
        return

    today = datetime.date.today()
    current_month_transactions = [
        t for t in transactions if t.date.year == today.year and t.date.month == today.month and t.type == "Expense"
    ]

    table = Table(title="Budget vs Spending")
    table.add_column("Category", style="cyan")
    table.add_column("Budget", justify="right", style="bold")
    table.add_column("Spent", justify="right", style="bold")
    table.add_column("Remaining", justify="right", style="bold")
    table.add_column("Utilization", justify="center")

    for category, budget in budgets.items():
        spent = sum(t.amount for t in current_month_transactions if t.category == category)
        remaining = budget.amount - spent
        utilization = (spent / budget.amount) * 100 if budget.amount > 0 else 0

        budget_str = f"{budget.amount / 100:.2f}"
        spent_str = f"{spent / 100:.2f}"
        remaining_str = f"{remaining / 100:.2f}"

        color = "green"
        if utilization > 100:
            color = "red"
        elif utilization > 70:
            color = "yellow"

        progress = ProgressBar(total=100, completed=utilization, width=20)

        table.add_row(
            category,
            budget_str,
            Text(spent_str, style=color),
            remaining_str,
            progress,
        )

    console.print(table)

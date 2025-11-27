
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

def load_budgets(console):
    """Loads budgets from the file."""
    global budgets
    try:
        with open(BUDGETS_FILE, "r") as f:
            data = json.load(f)
            budgets = {b["category"]: Budget(b["category"], b["amount"]) for b in data}
    except FileNotFoundError:
        budgets = {} # Silently handle if file doesn't exist
    except json.JSONDecodeError:
        budgets = {}
        console.print("[bold red]Error: The budgets file is corrupt and could not be loaded. Please check or delete budgets.txt.[/bold red]")
    except Exception as e:
        budgets = {}
        console.print(f"[bold red]An unexpected error occurred while loading budgets: {e}[/bold red]")

def save_budgets():
    """Saves budgets to the file."""
    try:
        with open(BUDGETS_FILE, "w") as f:
            json.dump([b.to_dict() for b in budgets.values()], f, indent=4)
    except IOError as e:
        console.print(f"[bold red]Error: Could not save budgets to file '{BUDGETS_FILE}'. Reason: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred while saving budgets: {e}[/bold red]")

def _validate_budget_amount(text):
    if not text:
        return "Amount cannot be empty."
    try:
        amount = float(text)
        if amount <= 0:
            return "Amount must be a positive number."
        return True
    except ValueError:
        return "Please enter a valid number."

def set_budget():
    """Sets a monthly budget for a category."""
    console = Console()
    load_budgets(console)
    try:
        category = questionary.select(
            "Select a category to budget:",
            choices=BUDGET_CATEGORIES,
            qmark="[?]"
        ).ask()
        if category is None: return

        amount_str = questionary.text(
            f"Enter the monthly budget for {category}:",
            validate=_validate_budget_amount,
            qmark="[?]"
        ).ask()
        if amount_str is None: return

        amount = int(float(amount_str) * 100)

        budgets[category] = Budget(category, amount)
        save_budgets()
        console.print(f"[bold green]Budget for {category} set to {amount / 100:.2f}[/bold green]")
    except (ValueError, TypeError):
        # This is less likely to be triggered now with better validation, but kept as a fallback
        console.print("[bold red]Invalid input. Please try again.[/bold red]")

from rich.text import Text

def view_budgets():
    """Views budget vs actual spending."""
    from features.transactions.transactions import transactions, load_transactions
    console = Console()
    load_budgets(console)
    load_transactions()
    

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

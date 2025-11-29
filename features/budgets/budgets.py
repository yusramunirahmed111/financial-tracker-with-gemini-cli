import json
import questionary
from rich.console import Console
from rich.text import Text

# In-memory budget storage
budgets = {}
BUDGETS_FILE = "database/budgets.txt"

BUDGET_CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Entertainment", "Health", "Other"
]


class Budget:
    def __init__(self, category, amount):
        self.category = category
        self.amount = amount  # stored in paisa/cents

    def to_dict(self):
        return {
            "category": self.category,
            "amount": self.amount
        }


# ============= STREAMLIT-COMPATIBLE VERSION =============
def load_budgets():
    """Loads budgets from file (Streamlit safe)."""
    global budgets
    try:
        with open(BUDGETS_FILE, "r") as f:
            data = json.load(f)
            budgets = {b["category"]: Budget(b["category"], b["amount"]) for b in data}
    except (FileNotFoundError, json.JSONDecodeError):
        budgets = {}
    except Exception:
        budgets = {}


def save_budgets():
    """Saves budgets to file safely."""
    try:
        with open(BUDGETS_FILE, "w") as f:
            json.dump([b.to_dict() for b in budgets.values()], f, indent=4)
    except Exception:
        pass


# ============= CLI BUDGET FUNCTIONS =============
def _validate_amount(text):
    try:
        value = float(text)
        if value <= 0:
            return "Amount must be positive."
        return True
    except:
        return "Enter a valid number."


def set_budget():
    console = Console()
    load_budgets()

    category = questionary.select(
        "Select category:",
        choices=BUDGET_CATEGORIES
    ).ask()

    if category is None:
        return

    amount_str = questionary.text(
        f"Enter monthly budget for {category}:",
        validate=_validate_amount
    ).ask()

    if amount_str is None:
        return

    amount = int(float(amount_str) * 100)

    budgets[category] = Budget(category, amount)
    save_budgets()

    console.print(f"[bold green]Budget set for {category}: Rs {amount / 100:.2f}[/bold green]")


def view_budgets():
    console = Console()
    load_budgets()

    if not budgets:
        console.print("[yellow]No budgets set yet.[/yellow]")
        return

    for cat, b in budgets.items():
        console.print(f"{cat}: Rs {b.amount / 100:.2f}")

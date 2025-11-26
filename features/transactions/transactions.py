import datetime
import json
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# In-memory database for transactions
transactions = []
TRANSACTIONS_FILE = "database/transactions.txt"

# Transaction categories
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

class Transaction:
    def __init__(self, date, transaction_type, category, description, amount):
        self.date = date
        self.type = transaction_type
        self.category = category
        self.description = description
        self.amount = amount  # Stored as an integer (paisa/cents)

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "type": self.type,
            "category": self.category,
            "description": self.description,
            "amount": self.amount
        }

def load_transactions():
    """Loads transactions from the file."""
    global transactions
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            data = json.load(f)
            transactions = [Transaction(
                datetime.datetime.fromisoformat(t["date"]).date(),
                t["type"],
                t["category"],
                t["description"],
                t["amount"]
            ) for t in data]
    except (FileNotFoundError, json.JSONDecodeError):
        transactions = []

def save_transactions():
    """Saves transactions to the file."""
    with open(TRANSACTIONS_FILE, "w") as f:
        json.dump([t.to_dict() for t in transactions], f, indent=4)

def add_expense():
    """Adds an expense transaction."""
    console = Console()
    try:
        amount_str = questionary.text(
            "Enter the expense amount:",
            validate=lambda text: text.isdigit() and float(text) > 0,
            qmark="[?]"
        ).ask()
        if amount_str is None: return

        amount = int(float(amount_str) * 100)

        category = questionary.select(
            "Select an expense category:",
            choices=EXPENSE_CATEGORIES,
            qmark="[?]"
        ).ask()
        if category is None: return

        description = questionary.text("Enter a description:", qmark="[?]").ask()
        if description is None: return

        date_str = questionary.text(
            "Enter the date (YYYY-MM-DD) or leave blank for today:",
            validate=lambda text: text == "" or datetime.datetime.strptime(text, "%Y-%m-%d"),
            qmark="[?]"
        ).ask()
        if date_str is None: return

        date = datetime.datetime.now().date() if not date_str else datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        new_transaction = Transaction(date, "Expense", category, description, amount)
        transactions.append(new_transaction)
        save_transactions()
        console.print("[bold green]Expense added successfully![/bold green]")
    except (ValueError, TypeError):
        console.print("[bold red]Invalid input. Please try again.[/bold red]")

def add_income():
    """Adds an income transaction."""
    console = Console()
    try:
        amount_str = questionary.text(
            "Enter the income amount:",
            validate=lambda text: text.isdigit() and float(text) > 0,
            qmark="[?]"
        ).ask()
        if amount_str is None: return

        amount = int(float(amount_str) * 100)

        category = questionary.select(
            "Select an income category:",
            choices=INCOME_CATEGORIES,
            qmark="[?]"
        ).ask()
        if category is None: return

        description = questionary.text("Enter a description:", qmark="[?]").ask()
        if description is None: return

        date_str = questionary.text(
            "Enter the date (YYYY-MM-DD) or leave blank for today:",
            validate=lambda text: text == "" or datetime.datetime.strptime(text, "%Y-%m-%d"),
            qmark="[?]"
        ).ask()
        if date_str is None: return

        date = datetime.datetime.now().date() if not date_str else datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        new_transaction = Transaction(date, "Income", category, description, amount)
        transactions.append(new_transaction)
        save_transactions()
        console.print("[bold green]Income added successfully![/bold green]")
    except (ValueError, TypeError):
        console.print("[bold red]Invalid input. Please try again.[/bold red]")

def list_transactions():
    """Lists all transactions."""
    load_transactions()
    console = Console()

    if not transactions:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
        return

    filter_choice = questionary.select(
        "Filter transactions by:",
        choices=["All", "Last 7 days", "Expenses only", "Income only"],
        qmark="[?]"
    ).ask()

    filtered_transactions = transactions
    today = datetime.date.today()

    if filter_choice == "Last 7 days":
        seven_days_ago = today - datetime.timedelta(days=7)
        filtered_transactions = [t for t in transactions if t.date >= seven_days_ago]
    elif filter_choice == "Expenses only":
        filtered_transactions = [t for t in transactions if t.type == "Expense"]
    elif filter_choice == "Income only":
        filtered_transactions = [t for t in transactions if t.type == "Income"]

    table = Table(title="Transactions")
    table.add_column("Date", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Category", style="yellow")
    table.add_column("Description", style="green")
    table.add_column("Amount", justify="right", style="bold")

    for t in sorted(filtered_transactions, key=lambda x: x.date, reverse=True):
        amount_str = f"{t.amount / 100:.2f}"
        style = "red" if t.type == "Expense" else "green"
        table.add_row(
            t.date.strftime("%Y-%m-%d"),
            t.type,
            t.category,
            t.description,
            Text(amount_str, style=style)
        )
    
    console.print(table)

from rich.text import Text
def show_balance():
    """Shows the current balance for the current month."""
    load_transactions()
    console = Console()

    today = datetime.date.today()
    current_month_transactions = [
        t for t in transactions if t.date.year == today.year and t.date.month == today.month
    ]

    total_income = sum(t.amount for t in current_month_transactions if t.type == "Income")
    total_expenses = sum(t.amount for t in current_month_transactions if t.type == "Expense")
    balance = total_income - total_expenses

    total_income_str = f"{total_income / 100:.2f}"
    total_expenses_str = f"{total_expenses / 100:.2f}"
    balance_str = f"{balance / 100:.2f}"

    balance_style = "green" if balance >= 0 else "red"

    panel = Panel(
        f"[green]Total Income: {total_income_str}[/green]\n"
        f"[red]Total Expenses: {total_expenses_str}[/red]\n"
        f"[{balance_style}]Current Balance: {balance_str}[/{balance_style}]",
        title="Current Month Balance",
        border_style="blue"
    )
    console.print(panel)

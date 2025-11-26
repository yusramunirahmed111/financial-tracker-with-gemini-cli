
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from features.transactions.transactions import (
    add_expense,
    add_income,
    list_transactions,
    show_balance,
)
from features.analytics.analytics import display_analytics_menu
from features.smart_assistant.smart_assistant import display_smart_assistant_menu
from features.data_management.data_management import display_data_management_menu

console = Console()

def display_welcome_message():
    welcome_text = Text("Welcome to Personal Finance Tracker CLI!", justify="center", style="bold green")
    console.print(Panel(welcome_text, border_style="blue"))

def manage_transactions():
    while True:
        choice = questionary.select(
            "Transaction Management",
            choices=[
                "Add Expense",
                "Add Income",
                "List Transactions",
                "Show Balance",
                "Back to Main Menu"
            ]
        ).ask()

        if choice == "Add Expense":
            add_expense()
        elif choice == "Add Income":
            add_income()
        elif choice == "List Transactions":
            list_transactions()
        elif choice == "Show Balance":
            show_balance()
        elif choice == "Back to Main Menu":
            break

def manage_analytics():
    display_analytics_menu()

def main_menu():
    while True:
        display_welcome_message()
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Manage Transactions",
                "Manage Budgets",
                "View Analytics",
                "Smart Assistant",
                "Data Management",
                "Exit"
            ]
        ).ask()

        if choice == "Manage Transactions":
            manage_transactions()
        elif choice == "Manage Budgets":
            # Call budget management function
            console.print("Managing Budgets...")
            pass
        elif choice == "View Analytics":
            manage_analytics()
        elif choice == "Smart Assistant":
            display_smart_assistant_menu()
        elif choice == "Data Management":
            display_data_management_menu()
        elif choice == "Exit":
            console.print(Panel(Text("Thank you for using Personal Finance Tracker!", justify="center", style="bold green"), border_style="blue"))
            break

if __name__ == "__main__":
    main_menu()

# Critical Money Handling Rule:
# ALWAYS store monetary values as integers (paisa/cents) to avoid floating-point errors.
# Example: Store Rs 12.50 as 1250 paisa. Display as amount / 100.
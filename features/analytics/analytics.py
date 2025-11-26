
import questionary
import datetime
import json
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.bar import Bar

from features.budgets.budgets import BUDGET_CATEGORIES, Budget, load_budgets as load_budgets_data, BUDGETS_FILE as BUDGETS_FILE_PATH

console = Console()

# In-memory database for transactions (will be loaded from file)
transactions = []
budgets = {}

TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = BUDGETS_FILE_PATH

# Transaction categories (copied from transactions.py to avoid circular imports or complex dependency management for now)
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

def spending_analysis():
    load_transactions()
    expenses = [t for t in transactions if t.type == "Expense"]

    if not expenses:
        console.print(Panel(Text("No expenses recorded yet.", style="bold yellow"), border_style="yellow"))
        return

    # Calculate total spending per category
    category_spending = defaultdict(int)
    total_spending = 0
    for expense in expenses:
        category_spending[expense.category] += expense.amount
        total_spending += expense.amount

    console.print(Panel(Text("Spending Analysis", justify="center", style="bold green"), border_style="green"))

    # ASCII Pie Chart / Breakdown by category
    console.print("\n[bold blue]Spending by Category:[/bold blue]")
    for category, amount in sorted(category_spending.items(), key=lambda item: item[1], reverse=True):
        percentage = (amount / total_spending) * 100
        bar_length = int(percentage / 2)  # Scale to 50 characters
        console.print(f"{category:<15} {'█' * bar_length} {percentage:.1f}% ({amount / 100:.2f})")

    # Top 3 spending categories
    sorted_categories = sorted(category_spending.items(), key=lambda item: item[1], reverse=True)
    console.print("\n[bold blue]Top 3 Spending Categories:[/bold blue]")
    for i, (category, amount) in enumerate(sorted_categories[:3]):
        console.print(f"{i+1}. {category}: {amount / 100:.2f}")

    # Average daily expense (for the current month)
    today = datetime.date.today()
    current_month_expenses = [e for e in expenses if e.date.year == today.year and e.date.month == today.month]
    if current_month_expenses:
        first_day_of_month = today.replace(day=1)
        days_in_month_so_far = (today - first_day_of_month).days + 1
        monthly_total_expense = sum(e.amount for e in current_month_expenses)
        average_daily_expense = (monthly_total_expense / days_in_month_so_far) / 100
        console.print(f"\n[bold blue]Average Daily Expense (Current Month):[/bold blue] {average_daily_expense:.2f}")
    else:
        console.print("\n[bold yellow]No expenses this month to calculate average daily expense.[/bold yellow]")

    console.print("\n[bold blue]Comparison with Last Month:[/bold blue] (Coming Soon)")
    console.print("[bold blue]Spending Trends:[/bold blue] (Coming Soon)")

def income_analysis():
    load_transactions()
    incomes = [t for t in transactions if t.type == "Income"]

    if not incomes:
        console.print(Panel(Text("No income recorded yet.", style="bold yellow"), border_style="yellow"))
        return

    # Calculate total income per category (source)
    category_income = defaultdict(int)
    total_income_current_month = 0
    today = datetime.date.today()
    
    # Calculate income for the current month
    for income in incomes:
        if income.date.year == today.year and income.date.month == today.month:
            category_income[income.category] += income.amount
            total_income_current_month += income.amount

    console.print(Panel(Text("Income Analysis", justify="center", style="bold green"), border_style="green"))

    # Income by source for the current month
    console.print("\n[bold blue]Income by Source (Current Month):[/bold blue]")
    for category, amount in sorted(category_income.items(), key=lambda item: item[1], reverse=True):
        console.print(f"{category:<15}: {amount / 100:.2f}")

    console.print(f"\n[bold blue]Total Income (Current Month):[/bold blue] {total_income_current_month / 100:.2f}")

    # Comparison with last month
    last_month = today.replace(day=1) - datetime.timedelta(days=1)
    total_income_last_month = sum(
        t.amount for t in incomes
        if t.date.year == last_month.year and t.date.month == last_month.month
    )

    console.print(f"[bold blue]Total Income (Last Month):[/bold blue] {total_income_last_month / 100:.2f}")

    if total_income_last_month > 0:
        change = ((total_income_current_month - total_income_last_month) / total_income_last_month) * 100
        if change >= 0:
            console.print(f"[bold green]Month-over-month change:[/bold green] +{change:.2f}%")
        else:
            console.print(f"[bold red]Month-over-month change:[/bold red] {change:.2f}%")
    else:
        console.print("[bold yellow]No income last month for comparison.[/bold yellow]")


    console.print("[bold blue]Income Stability:[/bold blue] (Coming Soon)")

def savings_analysis():
    load_transactions()
    
    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    
    # Calculate total income and expenses for the current month
    current_month_income = sum(t.amount for t in transactions if t.type == "Income" and t.date >= current_month_start)
    current_month_expenses = sum(t.amount for t in transactions if t.type == "Expense" and t.date >= current_month_start)
    
    monthly_savings = current_month_income - current_month_expenses
    
    console.print(Panel(Text("Savings Analysis", justify="center", style="bold green"), border_style="green"))
    console.print(f"\n[bold blue]Monthly Savings (Current Month):[/bold blue] {monthly_savings / 100:.2f}")

    # Savings Rate
    if current_month_income > 0:
        savings_rate = (monthly_savings / current_month_income) * 100
        console.print(f"[bold blue]Savings Rate (Current Month):[/bold blue] {savings_rate:.2f}%")
    else:
        console.print("[bold yellow]No income this month to calculate savings rate.[/bold yellow]")

    # Savings Trend (last 3 months)
    console.print("\n[bold blue]Savings Trend (Last 3 Months):[/bold blue]")
    for i in range(3):
        month_offset = i
        
        # Calculate month start and end for the historical month
        # Move to the first day of the current month, then subtract `month_offset` months
        target_month_date = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1) - datetime.timedelta(days=30 * month_offset)
        target_month_start = target_month_date.replace(day=1)
        target_month_end = (target_month_start + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)


        # Filter transactions for the historical month
        month_income = sum(t.amount for t in transactions if t.type == "Income" and t.date >= target_month_start and t.date <= target_month_end)
        month_expenses = sum(t.amount for t in transactions if t.type == "Expense" and t.date >= target_month_start and t.date <= target_month_end)
        
        month_savings = month_income - month_expenses
        console.print(f"{target_month_start.strftime('%Y-%m')}: {month_savings / 100:.2f}")


    console.print("\n[bold blue]Savings Goal Progress:[/bold blue] (Coming Soon)")

def financial_health_score():
    load_transactions()
    load_budgets_data()
    
    today = datetime.date.today()
    current_month_start = today.replace(day=1)

    # Calculate current month's income and expenses
    current_month_income_transactions = [t for t in transactions if t.type == "Income" and t.date >= current_month_start]
    current_month_expense_transactions = [t for t in transactions if t.type == "Expense" and t.date >= current_month_start]

    total_income = sum(t.amount for t in current_month_income_transactions)
    total_expenses = sum(t.amount for t in current_month_expense_transactions)

    score = 0
    score_breakdown = {}

    # 1. Savings Rate (30 points)
    monthly_savings = total_income - total_expenses
    if total_income > 0:
        savings_rate = (monthly_savings / total_income) * 100
        if savings_rate >= 20: # Aim for 20% savings rate
            score += 30
            score_breakdown["Savings Rate"] = {"score": 30, "detail": f"Excellent ({savings_rate:.2f}%)"}
        elif savings_rate >= 10:
            score += 20
            score_breakdown["Savings Rate"] = {"score": 20, "detail": f"Good ({savings_rate:.2f}%)"}
        else:
            score_breakdown["Savings Rate"] = {"score": 0, "detail": f"Low ({savings_rate:.2f}%) - Aim for at least 10-20%"}
    else:
        score_breakdown["Savings Rate"] = {"score": 0, "detail": "No income to calculate savings rate."}

    # 2. Budget Adherence (25 points)
    budget_adherence_score = 0
    if budgets:
        total_budgeted = sum(b.amount for b in budgets.values())
        total_spent_on_budgeted_categories = 0
        for category, budget_obj in budgets.items():
            spent = sum(t.amount for t in current_month_expense_transactions if t.category == category)
            if spent <= budget_obj.amount:
                total_spent_on_budgeted_categories += spent
            else:
                total_spent_on_budgeted_categories += budget_obj.amount # Only count up to budget for adherence
        
        if total_budgeted > 0:
            utilization = (total_spent_on_budgeted_categories / total_budgeted) * 100
            if utilization <= 80: # Spent 80% or less of budget
                budget_adherence_score = 25
                score_breakdown["Budget Adherence"] = {"score": 25, "detail": f"Excellent ({utilization:.2f}% utilized)"}
            elif utilization <= 100:
                budget_adherence_score = 15
                score_breakdown["Budget Adherence"] = {"score": 15, "detail": f"Good ({utilization:.2f}% utilized)"}
            else:
                score_breakdown["Budget Adherence"] = {"score": 0, "detail": f"Over budget ({utilization:.2f}% utilized) - Review spending"}
        else:
            score_breakdown["Budget Adherence"] = {"score": 0, "detail": "No active budgets to calculate adherence."}
    else:
        score_breakdown["Budget Adherence"] = {"score": 0, "detail": "No budgets set."}
    score += budget_adherence_score

    # 3. Income vs Expenses (25 points)
    if total_income > total_expenses:
        score += 25
        score_breakdown["Income vs Expenses"] = {"score": 25, "detail": "Income exceeds expenses - Healthy!"}
    elif total_income == total_expenses:
        score += 10
        score_breakdown["Income vs Expenses"] = {"score": 10, "detail": "Income equals expenses - Room for improvement."}
    else:
        score_breakdown["Income vs Expenses"] = {"score": 0, "detail": "Expenses exceed income - Caution!"}

    # 4. Debt Management (20 points) - Placeholder
    score_breakdown["Debt Management"] = {"score": 0, "detail": "Not tracked in this version. (Assumed 0 points)"}


    console.print(Panel(Text("Financial Health Score", justify="center", style="bold green"), border_style="green"))
    console.print(f"\n[bold magenta]Overall Financial Health Score: {score}/100[/bold magenta]\n")

    console.print("[bold blue]Score Breakdown:[/bold blue]")
    for factor, data in score_breakdown.items():
        console.print(f"- {factor}: [bold]{data['score']} points[/bold] - {data['detail']}")

    console.print("\n[bold blue]Recommendations:[/bold blue]")
    if score < 50:
        console.print("- Focus on increasing income or significantly reducing expenses.")
        console.print("- Create and stick to a strict budget.")
    elif score < 75:
        console.print("- Review your budget for areas to save more.")
        console.print("- Consider setting financial goals like an emergency fund.")
    else:
        console.print("- Keep up the great work!")
        console.print("- Explore investment opportunities to grow your wealth.")

def comprehensive_report():
    load_transactions()
    load_budgets_data()

    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    last_month_end = current_month_start - datetime.timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    # --- Data Collection ---
    current_month_income_transactions = [t for t in transactions if t.type == "Income" and t.date >= current_month_start]
    current_month_expense_transactions = [t for t in transactions if t.type == "Expense" and t.date >= current_month_start]

    last_month_income_transactions = [t for t in transactions if t.type == "Income" and t.date >= last_month_start and t.date < current_month_start]
    last_month_expense_transactions = [t for t in transactions if t.type == "Expense" and t.date >= last_month_start and t.date < current_month_start]

    total_income_cm = sum(t.amount for t in current_month_income_transactions)
    total_expenses_cm = sum(t.amount for t in current_month_expense_transactions)
    total_income_lm = sum(t.amount for t in last_month_income_transactions)
    total_expenses_lm = sum(t.amount for t in last_month_expense_transactions)

    monthly_savings_cm = total_income_cm - total_expenses_cm
    monthly_savings_lm = total_income_lm - total_expenses_lm

    # Category spending for current month
    category_spending_cm = defaultdict(int)
    for expense in current_month_expense_transactions:
        category_spending_cm[expense.category] += expense.amount

    # Category income for current month
    category_income_cm = defaultdict(int)
    for income in current_month_income_transactions:
        category_income_cm[income.category] += income.amount

    console.print(Panel(Text(f"Comprehensive Financial Report - {today.strftime('%B %Y')}", justify="center", style="bold green"), border_style="green"))

    # --- 1. Monthly Overview ---
    console.print("\n[bold blue]1. Monthly Overview:[/bold blue]")
    console.print(f"  Total Income: {total_income_cm / 100:.2f}")
    console.print(f"  Total Expenses: {total_expenses_cm / 100:.2f}")
    console.print(f"  Net Savings: {monthly_savings_cm / 100:.2f}")

    # --- 2. Income Summary ---
    console.print("\n[bold blue]2. Income Summary:[/bold blue]")
    if category_income_cm:
        for category, amount in sorted(category_income_cm.items(), key=lambda item: item[1], reverse=True):
            console.print(f"  - {category}: {amount / 100:.2f}")
    else:
        console.print("  No income recorded this month.")
    
    income_trend = ""
    if total_income_lm > 0:
        if total_income_cm > total_income_lm:
            income_trend = f" (▲ {(total_income_cm - total_income_lm) / 100:.2f} from last month)"
        elif total_income_cm < total_income_lm:
            income_trend = f" (▼ {(total_income_lm - total_income_cm) / 100:.2f} from last month)"
    console.print(f"  Total Income: {total_income_cm / 100:.2f}{income_trend}")

    # --- 3. Expense Summary ---
    console.print("\n[bold blue]3. Expense Summary:[/bold blue]")
    if category_spending_cm:
        for category, amount in sorted(category_spending_cm.items(), key=lambda item: item[1], reverse=True):
            console.print(f"  - {category}: {amount / 100:.2f}")
        sorted_expenses = sorted(category_spending_cm.items(), key=lambda item: item[1], reverse=True)
        console.print(f"  Top Expense Category: {sorted_expenses[0][0]} ({sorted_expenses[0][1]/100:.2f})")
    else:
        console.print("  No expenses recorded this month.")

    expense_trend = ""
    if total_expenses_lm > 0:
        if total_expenses_cm < total_expenses_lm:
            expense_trend = f" (▼ {(total_expenses_lm - total_expenses_cm) / 100:.2f} from last month)"
        elif total_expenses_cm > total_expenses_lm:
            expense_trend = f" (▲ {(total_expenses_cm - total_expenses_lm) / 100:.2f} from last month)"
    console.print(f"  Total Expenses: {total_expenses_cm / 100:.2f}{expense_trend}")

    # --- 4. Budget Performance ---
    console.print("\n[bold blue]4. Budget Performance:[/bold blue]")
    if budgets:
        over_budget_categories = []
        for category, budget_obj in budgets.items():
            spent = sum(t.amount for t in current_month_expense_transactions if t.category == category)
            if spent > budget_obj.amount:
                over_budget_categories.append(f"{category} (Spent: {spent/100:.2f}, Budget: {budget_obj.amount/100:.2f})")
        
        if over_budget_categories:
            console.print("[bold red]  Categories Over Budget:[/bold red]")
            for cat in over_budget_categories:
                console.print(f"    - {cat}")
        else:
            console.print("  All categories are within budget! Well done.")
    else:
        console.print("  No budgets set for performance analysis.")

    # --- 5. Savings Achieved ---
    console.print("\n[bold blue]5. Savings Achieved:[/bold blue]")
    if total_income_cm > 0:
        savings_rate_cm = (monthly_savings_cm / total_income_cm) * 100
        console.print(f"  Monthly Savings: {monthly_savings_cm / 100:.2f}")
        console.print(f"  Savings Rate: {savings_rate_cm:.2f}%")
    else:
        console.print("  No income this month to calculate savings.")
    
    # --- 6. Next Month Projections (Placeholder) ---
    console.print("\n[bold blue]6. Next Month Projections:[/bold blue]")
    console.print("  Based on current spending and income, aim to maintain or improve savings.")
    console.print("  Review categories where you overspent and consider adjustments.")


def display_analytics_menu():
    while True:
        choice = questionary.select(
            "Financial Analytics",
            choices=[
                "Spending Analysis",
                "Income Analysis",
                "Savings Analysis",
                "Financial Health Score",
                "Comprehensive Report",
                "Back to Main Menu"
            ]
        ).ask()

        if choice == "Spending Analysis":
            spending_analysis()
        elif choice == "Income Analysis":
            income_analysis()
        elif choice == "Savings Analysis":
            savings_analysis()
        elif choice == "Financial Health Score":
            financial_health_score()
        elif choice == "Comprehensive Report":
            comprehensive_report()
        elif choice == "Back to Main Menu":
            break

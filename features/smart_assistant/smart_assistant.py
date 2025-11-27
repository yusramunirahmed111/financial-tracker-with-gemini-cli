
import questionary
import datetime
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from features.analytics.analytics import load_transactions, transactions
from features.budgets.budgets import load_budgets, budgets

console = Console()

# Goals storage
GOALS_FILE = "database/goals.txt"
goals = {}

def load_goals():
    global goals
    try:
        with open(GOALS_FILE, "r") as f:
            data = json.load(f)
            goals = data
    except (FileNotFoundError, json.JSONDecodeError):
        goals = {}

def save_goals():
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=4)

def daily_financial_check():
    load_transactions()
    load_budgets(console)

    today = datetime.date.today()
    
    # Today's spending
    todays_expenses = sum(t.amount for t in transactions if t.type == "Expense" and t.date == today)
    
    # Remaining daily budget
    total_monthly_budget = sum(b.amount for b in budgets.values())
    days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - datetime.timedelta(days=1)).day
    avg_daily_budget = total_monthly_budget / days_in_month if days_in_month > 0 else 0
    remaining_daily_budget = (avg_daily_budget - todays_expenses) / 100

    console.print(Panel(Text(f"📊 Daily Financial Check ({today.strftime('%b %d, %Y')})", justify="center", style="bold green"), border_style="green"))
    console.print(f"\nToday's Spending: Rs {todays_expenses / 100:.2f}")
    
    status_emoji = "✅" if remaining_daily_budget >= 0 else "❌"
    console.print(f"Daily Budget: Rs {avg_daily_budget / 100:.2f} {status_emoji}")
    console.print(f"Remaining: Rs {remaining_daily_budget:.2f}")

    console.print("\n⚠️  Alerts: (Coming Soon)")
    console.print("\n💡 Tip: You're on track! Consider moving Rs 500 to savings. (Static for now)")

def generate_smart_recommendations():
    load_transactions()
    load_budgets(console)

    today = datetime.date.today()
    current_month_start = today.replace(day=1)

    recommendations = []

    # Calculate current month's income and expenses for savings rate
    current_month_income = sum(t.amount for t in transactions if t.type == "Income" and t.date >= current_month_start)
    current_month_expenses = sum(t.amount for t in transactions if t.type == "Expense" and t.date >= current_month_start)
    monthly_savings = current_month_income - current_month_expenses
    savings_rate = (monthly_savings / current_month_income) * 100 if current_month_income > 0 else 0

    # 1. Low savings
    if savings_rate < 10 and current_month_income > 0:
        recommendations.append("Low savings rate. Try to save at least 10-20% of your income.")
        recommendations.append("Consider the 50/30/20 rule: 50% for needs, 30% for wants, 20% for savings/debt.")

    # 2. Overspending categories
    from collections import defaultdict # Added import
    expense_categories_spending = defaultdict(int)
    for t in transactions:
        if t.type == "Expense" and t.date >= current_month_start:
            expense_categories_spending[t.category] += t.amount
    
    for category, spent in expense_categories_spending.items():
        if category in budgets and budgets[category].amount > 0:
            if spent > budgets[category].amount * 1.1: # 10% over budget
                recommendations.append(f"You are overspending in '{category}'. Consider reducing spending in this area.")
            elif spent > budgets[category].amount * 0.9: # Approaching budget limit
                recommendations.append(f"You are close to your budget limit in '{category}'. Be mindful of spending.")
        elif category not in budgets and spent > 0:
             recommendations.append(f"Consider setting a budget for '{category}' as you have significant spending there.")
            
    # 3. No budget set
    if not budgets:
        recommendations.append("No budgets set. Setting budgets can help you control your spending.")

    # 4. Good performance
    if savings_rate >= 20 and all(spent <= budgets[cat].amount for cat, spent in expense_categories_spending.items() if cat in budgets):
        recommendations.append("Excellent financial performance! Consider increasing your savings goals or exploring investments.")

    console.print(Panel(Text("Smart Recommendations", justify="center", style="bold green"), border_style="green"))
    if recommendations:
        for i, rec in enumerate(recommendations):
            console.print(f"💡 {i+1}. {rec}")
    else:
        console.print("[bold yellow]No specific recommendations at this moment. You're doing great![/bold yellow]")

def check_spending_alerts():
    load_transactions()
    load_budgets(console)

    alerts = []
    today = datetime.date.today()
    current_month_start = today.replace(day=1)

    # Calculate current month's income for large transaction alerts
    total_income_current_month = sum(t.amount for t in transactions if t.type == "Income" and t.date >= current_month_start)

    # 1. Budget warnings
    from collections import defaultdict # Added import
    current_month_expenses = [t for t in transactions if t.type == "Expense" and t.date >= current_month_start]
    category_spending_cm = defaultdict(int)
    for expense in current_month_expenses:
        category_spending_cm[expense.category] += expense.amount
    
    for category, budget_obj in budgets.items():
        spent = category_spending_cm[category]
        if budget_obj.amount > 0:
            utilization = (spent / budget_obj.amount) * 100
            if utilization >= 100:
                alerts.append(f"⚠️  Budget ALERT: '{category}' is {utilization:.0f}% used! (Spent: {spent / 100:.2f}, Budget: {budget_obj.amount / 100:.2f})")
            elif utilization >= 80:
                alerts.append(f"🔔 Budget WARNING: '{category}' is {utilization:.0f}% used. Approaching limit! (Spent: {spent / 100:.2f}, Budget: {budget_obj.amount / 100:.2f})")

    # 2. Large transaction alerts (>20% of monthly income)
    large_transaction_threshold = (total_income_current_month * 0.20) if total_income_current_month > 0 else 0
    for t in current_month_expenses:
        if t.amount >= large_transaction_threshold and large_transaction_threshold > 0:
            alerts.append(f"⚡ Large Transaction ALERT: Expense of {t.amount / 100:.2f} in '{t.category}' on {t.date.strftime('%Y-%m-%d')}.")

    console.print(Panel(Text("Spending Alerts System", justify="center", style="bold green"), border_style="green"))
    if alerts:
        for alert in alerts:
            console.print(alert)
    else:
        console.print("[bold green]No active spending alerts. Keep up the good work![/bold green]")
    
    console.print("\n[bold blue]Unusual spending patterns:[/bold blue] (Coming Soon)")
    console.print("[bold blue]Bill payment reminders:[/bold blue] (Coming Soon)")
    console.print("[bold blue]Savings milestones reached:[/bold blue] (Coming Soon)")

def analyze_savings_opportunities():
    load_transactions()
    load_budgets(console)

    opportunities = []
    today = datetime.date.today()
    current_month_start = today.replace(day=1)

    # Spending by category for the current month
    current_month_expenses = [t for t in transactions if t.type == "Expense" and t.date >= current_month_start]
    category_spending_cm = defaultdict(int)
    for expense in current_month_expenses:
        category_spending_cm[expense.category] += expense.amount
    
    total_monthly_spending = sum(category_spending_cm.values())

    console.print(Panel(Text("Savings Opportunities", justify="center", style="bold green"), border_style="green"))

    if not category_spending_cm:
        console.print("[bold yellow]No expenses recorded this month to analyze savings opportunities.[/bold yellow]")
        return
    
    console.print("\n[bold blue]Categories where spending can be reduced:[/bold blue]")
    sorted_spending = sorted(category_spending_cm.items(), key=lambda item: item[1], reverse=True)
    
    for category, spent_amount in sorted_spending:
        # Opportunity 1: Over budget categories
        if category in budgets and budgets[category].amount > 0 and spent_amount > budgets[category].amount:
            reduction_needed = spent_amount - budgets[category].amount
            opportunities.append(f"- '{category}': You are over budget by {reduction_needed / 100:.2f}. Consider reducing this amount.")
        # Opportunity 2: High spending categories (discretionary)
        elif spent_amount > total_monthly_spending * 0.15: # Arbitrary threshold for "high spending"
            opportunities.append(f"- '{category}': High spending ({spent_amount / 100:.2f}). Is there a way to cut back here?")
    
    if not opportunities:
        console.print("[bold green]No immediate savings opportunities identified based on current spending.[/bold green]")
    else:
        for opp in opportunities:
            console.print(opp)

    console.print("\n[bold blue]Estimated Monthly Savings Potential:[/bold blue]")
    # Simple estimation: 10% reduction in top 2 highest spending categories that are not essential bills
    estimated_potential = 0
    non_essential_categories = [cat for cat in sorted_spending if cat[0] not in ["Bills", "Health"]] # Example of non-essential
    for i, (category, spent_amount) in enumerate(non_essential_categories[:2]):
        potential_reduction = spent_amount * 0.10
        estimated_potential += potential_reduction
        console.print(f"- Reduce '{category}' spending by 10%: {potential_reduction / 100:.2f}")

    if estimated_potential > 0:
        console.print(f"\n[bold green]Total Estimated Monthly Savings Potential: {estimated_potential / 100:.2f}[/bold green]")
    else:
        console.print("[bold yellow]No significant monthly savings potential estimated at this time.[/bold yellow]")

    console.print("\n[bold blue]Compare with category averages:[/bold blue] (Coming Soon)")
    console.print("[bold blue]Show 'What if' scenarios:[/bold blue] (Coming Soon)")


def set_financial_goals():
    load_goals()
    console.print(Panel(Text("Set Financial Goals", justify="center", style="bold green"), border_style="green"))

    goal_type_choice = questionary.select(
        "Which type of goal would you like to set?",
        choices=["Emergency Fund", "Savings Target", "Debt Payoff", "Back"],
        qmark="[?]"
    ).ask()

    if goal_type_choice == "Back":
        return

    target_amount_str = questionary.text(
        "Enter target amount (e.g., 50000):",
        validate=lambda text: text.isdigit() and float(text) > 0,
        qmark="[?]"
    ).ask()
    if target_amount_str is None: return
    target_amount = int(float(target_amount_str) * 100)

    target_date_str = questionary.text(
        "Enter target date (YYYY-MM-DD):",
        validate=lambda text: text == "" or datetime.datetime.strptime(text, "%Y-%m-%d"),
        qmark="[?]"
    ).ask()
    if target_date_str is None: return
    target_date = target_date_str if target_date_str else ""

    if goal_type_choice == "Emergency Fund":
        goals["emergency_fund"] = {"type": "Emergency Fund", "target_amount": target_amount, "target_date": target_date}
        console.print("[bold green]Emergency Fund goal set successfully![/bold green]")
    elif goal_type_choice == "Savings Target":
        goals["savings_target"] = {"type": "Savings Target", "target_amount": target_amount, "target_date": target_date}
        console.print("[bold green]Savings Target goal set successfully![/bold green]")
    elif goal_type_choice == "Debt Payoff":
        current_debt_str = questionary.text(
            "Enter current debt amount (e.g., 10000):",
            validate=lambda text: text.isdigit() and float(text) >= 0,
            qmark="[?]"
        ).ask()
        if current_debt_str is None: return
        current_debt = int(float(current_debt_str) * 100)
        goals["debt_payoff"] = {"type": "Debt Payoff", "target_amount": target_amount, "current_debt": current_debt, "target_date": target_date}
        console.print("[bold green]Debt Payoff goal set successfully![/bold green]")
    
    save_goals()

def view_goals_progress():
    load_goals()
    load_transactions() # Needed for current savings calculation
    
    console.print(Panel(Text("🎯 Financial Goals Progress", justify="center", style="bold green"), border_style="green"))

    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    total_income_cm = sum(t.amount for t in transactions if t.type == "Income" and t.date >= current_month_start)
    total_expenses_cm = sum(t.amount for t in transactions if t.type == "Expense" and t.date >= current_month_start)
    current_savings_balance = total_income_cm - total_expenses_cm

    if not goals:
        console.print("[bold yellow]No goals set yet. Please set some financial goals![/bold yellow]")
        return
    
    for goal_key, goal_data in goals.items():
        console.print(f"\n[bold blue]{goal_data['type']}:[/bold blue]")
        target_amount = goal_data['target_amount'] / 100
        target_date_str = goal_data['target_date']
        
        current_progress = 0
        if goal_data['type'] == "Emergency Fund" or goal_data['type'] == "Savings Target":
            current_progress = max(0, current_savings_balance) / 100 # Assuming current savings contribute to these
        elif goal_data['type'] == "Debt Payoff":
            current_debt = goal_data['current_debt'] / 100
            current_progress = (target_amount - current_debt) # Progress is reduction from original debt to target. This needs refinement.

        percentage_achieved = (current_progress / target_amount) * 100 if target_amount > 0 else 0
        percentage_achieved = max(0, min(100, percentage_achieved)) # Cap between 0 and 100

        bar_length = int(percentage_achieved / 2) # Scale to 50 characters
        
        console.print(f"  [ {'█' * bar_length}{'░' * (50 - bar_length)} ] {percentage_achieved:.0f}% ({current_progress:.2f} / {target_amount:.2f})")
        console.print(f"  Expected: {target_date_str}")

def display_smart_assistant_menu():
    while True:
        choice = questionary.select(
            "Smart Financial Assistant",
            choices=[
                "Daily Financial Check",
                "Smart Recommendations",
                "Spending Alerts",
                "Savings Opportunities",
                "Set Financial Goals",
                "View Goals Progress",
                "Back to Main Menu"
            ]
        ).ask()

        if choice == "Daily Financial Check":
            daily_financial_check()
        elif choice == "Smart Recommendations":
            generate_smart_recommendations()
        elif choice == "Spending Alerts":
            check_spending_alerts()
        elif choice == "Savings Opportunities":
            analyze_savings_opportunities()
        elif choice == "Set Financial Goals":
            set_financial_goals()
        elif choice == "View Goals Progress":
            console.print(Panel(Text("Viewing Goals Progress...", justify="center", style="bold blue"), border_style="blue"))
            pass
        elif choice == "Back to Main Menu":
            break

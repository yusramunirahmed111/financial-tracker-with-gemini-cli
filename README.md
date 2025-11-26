# Personal Finance Tracker

A professional CLI and Web application for tracking expenses, income, budgets, and generating financial insights.

## Features

### CLI
- **Transaction Management**: Add expenses and income, list transactions, view current balance.
- **Budget Management**: Set monthly budgets for categories, track spending against them with utilization percentages and color-coded progress.
- **Financial Analytics**: Spending breakdown by category, top spending, average daily expense, income analysis, savings analysis, and a financial health score.
- **Smart Assistant**: Daily financial checks, smart recommendations, spending alerts, and savings opportunities.
- **Data Management**: Export transactions to CSV/JSON, export comprehensive monthly reports (JSON), import transactions from CSV, backup system, and data validation.

### Web Dashboard (Streamlit)
- **Balance Overview**: Displays current month's total income, expenses, and net balance.
- **Budget Status**: Shows budget vs. actual spending for each category with progress bars.
- **Recent Transactions**: A table of the most recent transactions.

## Tech Stack

-   **Language**: Python 3.11+
-   **CLI Framework**: Questionary (interactive select lists)
-   **UI Library**: Rich (tables, panels, progress bars for CLI)
-   **Web Framework**: Streamlit (for the web dashboard)
-   **Storage**: Plain text files (JSON format)
-   **Package Manager**: UV

## Getting Started

1.  **Clone the repository:**
    \`\`\`bash
    git clone <repository_url>
    cd personal-tracker
    \`\`\`

2.  **Install dependencies using UV:**
    \`\`\`bash
    uv pip install -r requirements.txt
    \`\`\`
    *(If you don't have UV, you can install it via `pip install uv`)*

3.  **Run the CLI Application:**
    \`\`\`bash
    python main.py
    \`\`\`

4.  **Run the Streamlit Web Dashboard:**
    \`\`\`bash
    streamlit run streamlit_dashboard.py
    \`\`\`
    This will open the dashboard in your web browser.

## Critical Money Handling Rule

**ALWAYS store monetary values as integers (paisa/cents) to avoid floating-point errors.**
Example: Store Rs 12.50 as 1250 paisa. Display as amount / 100.

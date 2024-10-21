# Spendwise

Spendwise is a finance management application designed to help users track their expenses, income, and financial preferences. It provides intuitive dashboards and diagrams for users to visualize and analyze their financial data. Spendwise allows users to manage their finances using any currency type, making it a versatile tool for users from different regions or those who handle multiple currencies.

## Features

1. Expense Tracking: Add, edit, and manage your daily expenses.
2. Income Management: Track multiple sources of income.
3. User Preferences: Set preferences for currencies, categories, and financial goals.
4. Dashboards: Interactive dashboards for visualizing expenses, income, and trends over time.
5. Currency Support: Manage and track finances in any currency with built-in currency conversion.
6. Secure Authentication: Manage user authentication securely with session-based login.
7. Modular Design: Designed with modularity and scalability in mind, allowing easy integration of new features.
Project Structure

## Installation

To run this project locally, follow these steps:

Clone the Repository:

1. git clone https://github.com/your-repository/spendwise.git
2. cd spendwise
3. Install Dependencies: Install the necessary Python dependencies using pip:
4. pip install -r requirements.txt
   
Setup Environment Variables: Rename the .env.example file to .env and provide the necessary environment variables such as the Postgres password, secret key, etc.
Database Configuration: By default, the project uses an SQLite database. To use Postgres, update your settings.py file with the appropriate database credentials:
python

Run Migrations: Migrate the database to create the necessary tables:
### python manage.py migrate
Run the Application: Start the development server:
### python manage.py runserver
### Access the Application: Open a browser and go to http://127.0.0.1:8000 to access Spendwise.

## Usage

1. Login/Register: Create an account or log in with your existing credentials.
2. Add Expenses: Navigate to the 'Expenses' section and add your expenses, categorize them, and set a currency. You can choose from a wide variety of currencies or add your custom currency.
3. Track Income: Go to the 'Income' section to track your various income streams.
4. Preferences: Set user preferences for categories, currencies (from a wide variety of global currencies), and goals.
5. Dashboard: View detailed analytics and charts of your financial data on the dashboard, available in your preferred currency.
Multi-Currency Support

Spendwise supports a wide range of currencies, allowing users to manage their finances in any currency of their choice. The system uses a currencies.json file to store exchange rates and can convert values between currencies on the fly, making it ideal for users with diverse financial needs.

## Contribution

1. Fork the repository
2. Create a feature branch
3. Make your changes and commit them
4. Push to your fork
5. Create a pull request

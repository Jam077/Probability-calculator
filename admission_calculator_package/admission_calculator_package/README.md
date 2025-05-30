# Admission Probability Calculator

This web application calculates admission probabilities for Azerbaijani universities based on historical passing scores.

## Features

- Input your expected score (0-700)
- Filter by group/education type (1-ci qrup, 2-ci qrup, Magistr, Kollec, etc.)
- Filter by language sector (Azerbaijani, Russian, English)
- Select how many top results to display (3, 5, 10, or 20)
- View probabilities calculated to two decimal places
- Secure login system to restrict access

## Installation

1. Ensure you have Python 3.8+ installed on your system
2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Navigate to the application directory
2. Run the Flask application:
   ```
   python -m src.main
   ```
3. Open your web browser and go to:
   ```
   http://localhost:5000
   ```
4. Log in with the following credentials:
   - Email: majidov@gmail.com
   - Password: password123

## Deployment Options

### Option 1: Local Deployment
Follow the installation and running instructions above.

### Option 2: PythonAnywhere Deployment
1. Create a PythonAnywhere account at https://www.pythonanywhere.com/
2. Upload this package to your PythonAnywhere account
3. Create a new web app with Flask
4. Set the source code directory to the location of this package
5. Set the WSGI configuration file to point to src.main:app
6. Install the requirements using PythonAnywhere's console

### Option 3: Heroku Deployment
1. Create a Heroku account at https://www.heroku.com/
2. Install the Heroku CLI
3. Create a new file named `Procfile` with the content:
   ```
   web: gunicorn src.main:app
   ```
4. Add `gunicorn` to requirements.txt
5. Deploy using the Heroku CLI:
   ```
   heroku login
   git init
   git add .
   git commit -m "Initial commit"
   heroku create
   git push heroku master
   ```

## Customizing Access Control

To modify the login credentials or implement more advanced access control:

1. Edit the `src/main.py` file
2. Locate the following lines:
   ```python
   # Authorized user credentials
   AUTHORIZED_USER = "majidov@gmail.com"
   AUTHORIZED_PASSWORD = "password123"
   ```
3. Update with your preferred credentials or implement a database-backed user system

## Data Source

The application uses historical passing score data stored in `src/static/merged_score_lists_final.xlsx`.

IRIS INSIGHT - Module 3 dependency-light dashboard
===================================================

This implementation is designed to avoid the previously blocked Pandas/NumPy native extensions.
It uses Python 3.14 standard-library modules and the PyMySQL package already present in the uploaded project's venv.
It does NOT import Pandas, NumPy, Streamlit, SQLAlchemy, or Flask.

INSTALLATION: none. No pip install command is required if the existing venv still contains PyMySQL.

FILES
- app.py: Python HTTP server, MySQL data access, KPI analytics, report execution, Ask Iris, query history
- templates/index.html: seven-section application shell
- static/styles.css: premium dark scientific SaaS design system
- static/app.js: navigation, Plotly charts, Three.js Iris model, filters and interactions
- run_dashboard.bat: Windows launcher using the existing project's venv\Scripts\python.exe
- tests/test_app.py: isolated application logic tests

WINDOWS LAUNCH
1. Copy the web_dashboard folder into the root of Iris_Species_Inventory_Dashboard.
2. Keep the existing .env file in the project root. The app reads DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME.
3. Double-click web_dashboard\run_dashboard.bat.
4. The browser opens at http://127.0.0.1:8765.

No PowerShell activation is used. The launcher does not reinstall packages, change Python, change Windows security settings, or modify the database schema.

TESTS
From the project root, run:
  venv\Scripts\python.exe -m unittest web_dashboard.tests.test_app -v

DATABASE NOTES
- Read-only MySQL queries only; no CREATE/ALTER/DELETE/UPDATE operations are issued against the scientific database.
- The six Overview KPIs follow the supplied design specification.
- R01-R10 use the existing SQL files; R10 uses the parameterized *_app.sql version.
- Query history is stored in local SQLite at data\app\query_history.sqlite3.
- Ask Iris supports a deliberately limited set of reviewed questions; unsupported questions are rejected.
- Quality-log and import-batch fields are discovered at runtime where optional schema fields are involved.

LIMITATIONS / VERIFICATION
- The Python HTTP/API logic and UI can be tested without the user's MySQL service, but live database integration must be confirmed on the user's computer.
- Plotly and Three.js are loaded from public CDNs; internet access is needed for those two visual libraries and the Google font. The rest of the application is local.
- Database status is shown as disconnected if the MySQL connection cannot be established; mock data is never substituted.

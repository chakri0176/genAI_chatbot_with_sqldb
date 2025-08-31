# 🐬 LangChain SQL Chatbot (Streamlit)
Chat with your databases (SQLite, MySQL, **SQL Server**) using a Groq-powered LLM (Llama 3.1 8B Instant) — all from a friendly Streamlit UI.

> Built with **LangChain** (SQL agent), **SQLAlchemy**, and **pyodbc/mysql-connector** for DB access.

---

## ✨ Features
- **Multi-DB support**: SQLite (read-only), MySQL, and Microsoft SQL Server (MSSQL)
- **MSSQL auth modes**: Windows Integrated (NTLM/Kerberos) **and** SQL Login (User ID/Password)
- **LLM reasoning over SQL** via LangChain’s SQL agent + `SQLDatabaseToolkit`
- **Streamed responses** in the chat UI
- **Session history** with a one-click “Clear message history” button

---

## 🧭 Project Structure
```
.
├── app.py           # Streamlit app (UI + agent + DB connectors)
├── company.db       # (Optional) Example SQLite DB — or place your own
└── README.md
```
> If you use SQLite, place the DB file next to `app.py` (see **Configuration → SQLite**).

---

## 🧰 Requirements
- **Python** 3.9+ (64‑bit recommended)
- **Packages** (install below)
- **Groq API key** (for the LLM)
- For **MSSQL**:
  - Microsoft **ODBC Driver 17 or 18 for SQL Server** (64‑bit)
  - Matching Python bitness (64‑bit Python ↔ 64‑bit driver)

### Install Python deps
```bash
# from your virtual env
pip install -U streamlit sqlalchemy pyodbc mysql-connector-python langchain langchain-groq langchain-community
```

> `sqlite3` is built into Python. On Windows you don’t need extra drivers for SQLite.

---

## 🔐 Configure credentials
### 1) Groq (LLM)
Set your key as an environment variable (recommended):
```powershell
# PowerShell
setx GROQ_API_KEY "your_groq_api_key_here"
```
Or paste it into the **sidebar** when the app runs.

### 2) Database access
- **MySQL**: host/user/password/db in the sidebar
- **MSSQL**:
  - Pick **Windows (Integrated)** if you authenticate with your Windows account (no User/Password fields)
  - Pick **SQL Login** to provide `User ID` + `Password`
  - Driver: choose the exact ODBC driver installed on your machine (e.g., `ODBC Driver 17 for SQL Server`)

> **Integrated auth note (Windows only):** The Streamlit **process identity** connects to SQL Server. Make sure that Windows user has access to the target database.

---

## ⚙️ Configuration details
### SQLite
- The app opens a **read-only** SQLite DB placed next to `app.py`.
- Update the filename if needed. The current code expects a file named `student.db` in the original version; in your latest file the path line shows `comapny.db` *(typo)* — see **Known issues** below.

### MySQL
- Uses SQLAlchemy’s `mysql+mysqlconnector://` URL underneath.
- Ensure port is open (default 3306) and the MySQL user has privileges on the DB.

### MSSSQL (SQL Server)
- Connection is built with an **ODBC connection string** via `pyodbc` + SQLAlchemy (`mssql+pyodbc:///?odbc_connect=...`)
- Works with:
  - `SERVER=HOST` or `HOST,PORT` (e.g., `localhost,1433`)
  - `HOST\INSTANCE` (requires SQL Browser service; otherwise prefer explicit port)
- TLS:
  - **Prod**: `Encrypt=yes;TrustServerCertificate=no;` (use a valid cert)
  - **Dev/Test**: you may temporarily set `TrustServerCertificate=yes`

---

## 🚀 Run the app
```bash
# from the project folder
streamlit run app.py
```
Then open the local URL shown by Streamlit (usually http://localhost:8501).

### Using the UI
1. Pick a database in the **sidebar**:
   - “Use SQLite 3 Database – student.db”
   - “Connect to your SQL Data (MySQL)”
   - “Connect to SQL Server (MSSQL)”
2. Fill connection fields (for MSSQL, pick auth mode and driver)
3. Provide your **GROQ API key**
4. Ask questions in the chat box (e.g., “Top 5 customers by revenue”)

---

## 🧠 How it works (high level)
```
User question → LangChain SQL Agent → (inspects schema) → Generates SQL →
Executes via SQLAlchemy/pyodbc → Returns rows → Agent summarizes → Streamlit UI
```

- **LangChain components** used:
  - `SQLDatabase` (DB wrapper)
  - `SQLDatabaseToolkit` (tools exposed to the agent)
  - `create_sql_agent` (Zero‑shot ReAct agent)
- **LLM**: Groq `llama-3.1-8b-instant` (streaming on)

---

## 🧪 Quick sanity checks (MSSQL)
### Check installed ODBC drivers (Python)
```python
import pyodbc, platform
print("Python:", platform.architecture())
print("Installed ODBC drivers:", pyodbc.drivers())
```
Pick one **exactly** as it appears (e.g., `ODBC Driver 17 for SQL Server`).

### Direct ODBC connect (Integrated auth)
```python
import pyodbc
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=HOST,1433;"            # or HOST\\INSTANCE
    "DATABASE=YourDb;"
    "Encrypt=yes;TrustServerCertificate=no;"
    "Trusted_Connection=yes;"
)
print("Connected!"); conn.close()
```

---

## 🧯 Troubleshooting
- **IM002: “Data source name not found and no default driver specified”**  
  → Wrong/missing driver name. Install Microsoft ODBC Driver **17 or 18** (64‑bit) and use the **exact** name from `pyodbc.drivers()`.

- **Login failed for user ‘DOMAIN\user’** (Integrated auth)  
  → Grant your Windows account a login/user in SQL Server and proper DB permissions.

- **Cannot generate SSPI context** (Kerberos)  
  → SPN/time sync/env issue. Often NTLM still works; try `HOST,PORT` instead of `HOST\\INSTANCE`. Check domain connectivity.

- **Timeout to HOST\\INSTANCE**  
  → SQL Browser not running / firewall. Prefer `HOST,PORT` (e.g., `HOST,1433`) or start SQL Browser.

- **TLS/Certificate errors**  
  → In dev, toggle “Trust Server Certificate (dev/test)” in the sidebar. In prod, use a valid certificate with `TrustServerCertificate=no`.

---

## 🧹 Known issues & quick fixes
- **Typos in UI text**: *“Chosse”*, *“SQLLite”* → purely cosmetic.
- **SQLite path typo**: code references `comapny.db`. Rename to `company.db` **or** change the path to `student.db` (your actual file name).
- **Variable name mismatch (MSSQL SQL Login)**: in the UI code `msssql_user` (3 s’s) is created, but later `mssql_user` is used. Rename consistently to `mssql_user` in both places.
- **ODBC Driver default**: If your machine only has **Driver 17**, choose that in the sidebar (or change the default).

> See **`app.py`** for the exact implementation. Please keep secrets out of source control.

---

## 🧪 Example prompts
- “List the 10 most recent orders with customer names”
- “Total revenue by month in 2024”
- “Which products have never been ordered?”
- “Top 5 customers by lifetime spend”

---

## 🛡️ Security notes
- Don’t commit API keys or DB passwords.
- Restrict DB user permissions to the minimum needed.
- In production, keep `Encrypt=yes;TrustServerCertificate=no` with a valid certificate.

---

## 🗺️ Roadmap
- [ ] Add Postgres support
- [ ] Per‑user auth in web deployments
- [ ] Schema inspector/render (ERD) in UI
- [ ] Caching of common answers

---

## 🤝 Contributing
Pull requests welcome! Please open an issue before large changes. Make sure to lint and add brief test notes.

---

## 📜 License
This project is released under **The Unlicense** (public domain dedication).

- You may use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies **without restrictions**.
- The software is provided **as-is, without warranty of any kind**. See the `LICENSE` file for the full text.
- **Collaboration is welcome!** Feel free to open issues and pull requests.


## 📎 Reference
This README accompanies the Streamlit app in `app.py`.

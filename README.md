# 🧠 GrabDocs — Intelligent Document Management Automated Tests

This repository contains automated **end-to-end tests** for [GrabDocs](https://app.grabdocs.com/), an intelligent document management platform.  
Tests are implemented using **Python**, **Pytest**, and **Playwright** to validate key user workflows such as authentication, workspace management, uploads, and chat functionality.

---

## 📁 Project Structure

```
├── Grabdocs Test Plan.pdf         # Reference document for test planning
├── logged_in.json                 # Stored login state (auto-generated)
├── README.md                      # Project documentation (this file)
├── requirements.txt               # Python dependencies (note: “tsxt” → typo fix)
└── tests/
    ├── conftest.py                # Pytest fixtures (setup, authentication)
    ├── test_auth.py               # Authentication and session tests
    ├── test_chat.py               # Chat-related test cases
    ├── test_files.py              # Files related test cases
    └── test_workspace.py          # Workspace creation and deletion tests
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/queendebra92/grabdocs_tests
cd grabdocs-tests
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # On Linux/macOS
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn’t exist yet, create it with:
```bash
pytest
playwright
pytest-playwright
python-dotenv
```

Then install Playwright browsers:
```bash
playwright install
```

---

## 🔐 Environment Variables

Set credentials used for logging into GrabDocs:

```bash
export EMAIL="your_email@example.com"
export PASSWORD="your_password"
```

Or create a `.env` file:
```
EMAIL=your_email@example.com
PASSWORD=your_password
```

---

## ▶️ Running the Tests

Run all tests:
```bash
pytest -v
```

Run a specific test file:
```bash
pytest tests/test_auth.py -v
```

Run tests in headed mode (browser visible):
```bash
pytest --headed
```

---

## 🧪 What the Tests Cover

| Test File | Description |
|------------|--------------|
| `test_auth.py` | Validates login, remember-me, and logout flow |
| `test_workspace.py` | Creates and deletes team workspaces |
| `test_chat.py` | Tests chat input and message visibility |
| `test_files.py` | Uploads files to the dashboard and validates success |

Each test reuses an **authenticated Playwright context** managed by `conftest.py`, preventing redundant logins and improving test efficiency.

---

## 🧰 Key Fixtures

| Fixture | Scope | Description |
|----------|--------|-------------|
| `base_url` | session | The GrabDocs app base URL |
| `email` / `password` | session | User credentials from environment |
| `browser_context` | session | Provides a single browser session |
| `authenticated_context` | session | Logs in and reuses an authenticated browser context |

---

## 📤 Upload Test Example

```python
page.set_input_files("input[type='file']", "Grabdocs Test Plan.pdf")
expect(page.get_by_text("No documents uploaded yet")).not_to_be_visible()
```

This test validates that file uploads successfully remove the "No documents uploaded yet" message on the **GrabDocs Upload** page.

---

## 🚀 GrabDocs

> **GrabDocs** — Intelligent Document Management  
> Automate document handling, chat with your data, and transform your workspace productivity.  
> [Visit GrabDocs →](https://app.grabdocs.com/)

---

## 🧹 Notes

- If `logged_in.json` exists, tests will reuse it for faster sessions.
- Some tests (e.g. “Remember Me”) may be known to fail due to unimplemented features in the current production environment.
- You can safely delete `logged_in.json` to force reauthentication.

---



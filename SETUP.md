# Setup — Dependencies (Simple)

This file provides very simple, copy-pastable commands to install the project's runtime dependencies on Windows. The repository includes an automated setup script `setup.bat` which will create a virtual environment named `env`, install dependencies, and run the database initialization. Use that for a one-step setup, or follow the manual commands below.

Prerequisites
- Python 3.11 or newer
- PostgreSQL (running)

Automated (recommended)

```powershell
# From repository root
setup.bat
```

The `setup.bat` script will:
- Check that `python` is available
- Create a virtual environment named `env` (if missing)
- Activate the environment (batch activation)
- Install dependencies from `requirements.txt`
- Run `python manage.py init_db` to initialize the database

Manual steps (PowerShell)

1. Create and activate a virtual environment (this mirrors what `setup.bat` creates)

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

2. Install Python dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3. Database (PostgreSQL)

- Ensure PostgreSQL is installed and the server is running.
- Configure the credentials in `config/settings.py` or create the database/user manually.

4. Initialize the project (if not using `setup.bat`)

```powershell
python manage.py init_db
python manage.py migrate
```

5. Create an admin user and start the dev server

```powershell
python manage.py createsuperuser
python manage.py runserver
```

Notes for Command Prompt (cmd.exe)

If you prefer using the Windows Command Prompt, activate the virtual environment with:

```cmd
env\Scripts\activate
```

Optional: Node.js frontend (only if you use a JS build step)

- If the project uses npm for front-end builds, install Node.js and run:

```powershell
# from project root (if package.json exists)
npm install
# then run any build step, e.g.:
npm run build
```

Notes & tips
- `setup.bat` creates a venv named `env` (not `.venv`). The README and automated script expect `env`.
- Use `git stash` (or commit) before switching branches to avoid losing uncommitted changes.
- Run PowerShell as Administrator only if you encounter permission issues when creating the DB or virtual environment.
- The automated `setup.bat` script performs most of these steps for convenience.

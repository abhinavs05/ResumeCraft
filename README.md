# ResumeCraft

ResumeCraft is a Django web application for creating and managing ATS-friendly resumes. It includes live previews, resume templates, PDF export, and an ATS keyword scan.

## Features

- Create an account and manage multiple resumes.
- Add personal details, education, experience, projects, skills, and achievements.
- Choose from five templates: Jake's, Modern, Creative, Corporate, and Academic.
- Preview, duplicate, and delete resumes.
- Export resumes as PDF or JSON, and import resume data from JSON.
- Compare a resume with a job description using the ATS scanner.

## Requirements

- Python 3.12 or newer
- pip

## Run locally

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   cd YOUR-REPOSITORY
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell, activate it with:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install the required packages:

   ```bash
   python -m pip install Django xhtml2pdf
   ```

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser and register an account.

The app uses SQLite by default and creates `db.sqlite3` in the project directory when migrations are applied.

## Admin account (optional)

To create a Django administrator account for `/admin/`, run:

```bash
python manage.py createsuperuser
```

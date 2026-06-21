# Job Portal Pro

A professional job portal built with Django where admins can post jobs and job seekers can apply.

## Features

### For Job Seekers
- Register/Login with email or Google
- Browse and search jobs
- Apply for jobs with resume and cover letter
- Track application status
- Update profile and upload resume
- Job recommendations based on skills
- Email notifications for application updates

### For Admins
- Comprehensive admin dashboard
- Post and manage job listings
- Review and manage applications
- Track application metrics and analytics
- User management
- Blog management
- Site settings management

## Tech Stack
- Django 4.2
- Bootstrap 5
- PostgreSQL/SQLite
- django-allauth (Authentication)
- CKEditor (Rich text editing)
- Chart.js (Analytics)
- Font Awesome (Icons)

## Setup Instructions

1. Clone the repository

- git clone <repository-url>
- cd job_portal


2. Setup Instructions

- python -m venv venv
- source venv/bin/activate  # On Windows: venv\Scripts\activate


3. Install dependencies

- pip install -r requirements.txt


4. Configure environment variables

- Copy .env.example to .env

- Update the values as needed

- For Google login, set up Google OAuth credentials


5. Run migrations

- python manage.py makemigrations
- python manage.py migrate


6. Create admin user

- python manage.py create_admin


7. Setup initial data

- python manage.py shell < setup.py


8. Collect static files

- python manage.py collectstatic


9. Run development server

- python manage.py runserver

## Visit:

- Main site: http://127.0.0.1:8000

- Admin panel: http://127.0.0.1:8000/admin

- Default admin: admin@jobportal.com / Admin@123


### Production Deployment
## For production:

- Set DEBUG=False in .env
- Use PostgreSQL database
- Configure proper email backend
- Set up proper static/media file serving
- Use Gunicorn + Nginx
- Enable HTTPS
- Set up proper Google OAuth credentials


## Google OAuth Setup
- Go to Google Cloud Console
- Create a new project
- Enable Google+ API
- Create OAuth 2.0 credentials
- Add authorized redirect URIs:
    - http://127.0.0.1:8000/accounts/google/login/callback/
- Add credentials to .env file

### License
## MIT License
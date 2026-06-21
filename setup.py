import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_portal.settings')
django.setup()

from core.models import SiteSettings
from jobs.models import JobCategory
from django.core.files.base import ContentFile

def setup_site_settings():
    """Create initial site settings"""
    if not SiteSettings.objects.exists():
        settings = SiteSettings.objects.create(
            site_name='JobPortal Pro',
            tagline='Find Your Dream Job Today',
            about_title='About JobPortal Pro',
            about_description='''
            <p>JobPortal Pro is your premier destination for finding the perfect job match. 
            We connect talented professionals with top employers across various industries.</p>
            <p>Our platform streamlines the job search process, making it easier than ever 
            to discover opportunities that align with your skills and career goals.</p>
            ''',
            mission='''
            <p>Our mission is to empower job seekers by providing them with the tools and 
            resources they need to find meaningful employment opportunities. We strive to 
            create a seamless bridge between talented individuals and organizations looking 
            to hire the best talent.</p>
            ''',
            vision='''
            <p>We envision a world where every professional can find a job that not only 
            matches their skills but also fulfills their career aspirations. We aim to be 
            the most trusted and efficient job portal, revolutionizing the way people find 
            employment.</p>
            ''',
            email='contact@jobportalpro.com',
            phone='+1 (555) 123-4567',
            address='123 Business Avenue, Suite 100, New York, NY 10001',
            facebook='https://facebook.com/jobportalpro',
            twitter='https://twitter.com/jobportalpro',
            linkedin='https://linkedin.com/company/jobportalpro',
            instagram='https://instagram.com/jobportalpro',
            meta_description='Find your dream job with JobPortal Pro. Browse thousands of job listings from top companies.',
            meta_keywords='jobs, careers, employment, job search, hiring, recruitment',
            primary_color='#0d6efd',
            secondary_color='#6c757d',
            footer_text='JobPortal Pro is the leading online job board connecting job seekers with employers.',
            copyright_text='© 2024 JobPortal Pro. All rights reserved.'
        )
        print('Site settings created successfully!')
    else:
        print('Site settings already exist.')

def create_job_categories():
    """Create default job categories"""
    categories = [
        {
            'name': 'Technology',
            'slug': 'technology',
            'description': 'Software development, IT, and tech-related jobs',
            'icon': 'fas fa-laptop-code'
        },
        {
            'name': 'Healthcare',
            'slug': 'healthcare',
            'description': 'Medical, nursing, and healthcare positions',
            'icon': 'fas fa-hospital'
        },
        {
            'name': 'Finance',
            'slug': 'finance',
            'description': 'Banking, accounting, and financial services',
            'icon': 'fas fa-chart-line'
        },
        {
            'name': 'Marketing',
            'slug': 'marketing',
            'description': 'Digital marketing, advertising, and PR roles',
            'icon': 'fas fa-bullhorn'
        },
        {
            'name': 'Sales',
            'slug': 'sales',
            'description': 'Sales and business development positions',
            'icon': 'fas fa-handshake'
        },
        {
            'name': 'Education',
            'slug': 'education',
            'description': 'Teaching, training, and educational roles',
            'icon': 'fas fa-graduation-cap'
        },
        {
            'name': 'Engineering',
            'slug': 'engineering',
            'description': 'Engineering and technical positions',
            'icon': 'fas fa-cogs'
        },
        {
            'name': 'Design',
            'slug': 'design',
            'description': 'UI/UX, graphic design, and creative roles',
            'icon': 'fas fa-palette'
        },
    ]
    
    for category in categories:
        JobCategory.objects.get_or_create(
            slug=category['slug'],
            defaults=category
        )
    
    print('Job categories created successfully!')

if __name__ == '__main__':
    setup_site_settings()
    create_job_categories()
    print('Setup completed!')
# Create in your app's migrations or a management command
from core.models import LegalPage

def create_default_legal_pages():
    pages = [
        {
            'title': 'Terms and Conditions',
            'slug': 'terms-and-conditions',
            'page_type': 'terms',
            'content': '<h2>Terms and Conditions</h2><p>Welcome to our website...</p>',
        },
        {
            'title': 'Privacy Policy',
            'slug': 'privacy-policy',
            'page_type': 'privacy',
            'content': '<h2>Privacy Policy</h2><p>Your privacy is important to us...</p>',
        },
        {
            'title': 'Cookie Policy',
            'slug': 'cookie-policy',
            'page_type': 'cookies',
            'content': '<h2>Cookie Policy</h2><p>This website uses cookies...</p>',
        },
    ]
    
    for page_data in pages:
        LegalPage.objects.get_or_create(
            slug=page_data['slug'],
            defaults=page_data
        )
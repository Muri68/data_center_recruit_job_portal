from core.models import SiteSettings, FAQ, WhyChooseUs

def site_settings(request):
    """Context processor to add site settings to all templates"""
    try:
        settings = SiteSettings.objects.first()
        faqs = FAQ.objects.filter(is_active=True).order_by('order')
        why_choose_us_features = WhyChooseUs.objects.filter(is_active=True).order_by('order')
    except:
        settings = None
        faqs = []
        why_choose_us_features = []
    
    context = {
        'site_settings': settings,
        'site_name': settings.site_name if settings else 'JobPortal Pro',
        'site_logo': settings.logo if settings else None,
        'site_favicon': settings.favicon if settings else None,
        'primary_color': settings.primary_color if settings else '#0d6efd',
        'secondary_color': settings.secondary_color if settings else '#6c757d',
        'faqs': faqs,
        'why_choose_us_features': why_choose_us_features,
    }
    
    return context
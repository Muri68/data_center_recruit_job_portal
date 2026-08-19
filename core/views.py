from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from .models import SiteSettings, LegalPage
from jobs.models import Job, JobCategory
from blog.models import BlogPost

def home(request):
    featured_jobs = Job.objects.filter(status='published', is_featured=True)[:6]
    recent_jobs = Job.objects.filter(status='published').order_by('-posted_at')[:8]
    categories = JobCategory.objects.all()
    recent_posts = BlogPost.objects.filter(status='published')[:3]
    
    # Job statistics
    total_jobs = Job.objects.filter(status='published').count()
    total_companies = Job.objects.filter(status='published').values('company_name').distinct().count()
    
    context = {
        'featured_jobs': featured_jobs,
        'recent_jobs': recent_jobs,
        'categories': categories,
        'recent_posts': recent_posts,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
    }
    return render(request, 'core/index.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Send email
        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        
        try:
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email=email,
                recipient_list=[SiteSettings.objects.first().email],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except:
            messages.error(request, 'Failed to send message. Please try again.')
        
        return redirect('core:contact')
    
    return render(request, 'core/contact.html')




def legal_page(request, slug):
    """Display a legal page"""
    page = get_object_or_404(LegalPage, slug=slug, is_active=True)
    
    context = {
        'page': page,
        'page_title': page.title,
        'meta_description': page.meta_description,
        'meta_keywords': page.meta_keywords,
    }
    return render(request, 'core/legal_page.html', context)



# core/views.py
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def error_401(request, exception=None):
    """Handle 401 Unauthorized errors"""
    logger.warning(f"401 error: {request.path}")
    if request.path.startswith('/api/'):
        from django.http import JsonResponse
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        return render(request, 'errors/401.html', status=401)
    except:
        return HttpResponseBadRequest('<h1>401 - Unauthorized</h1><p>You need to be logged in to access this page.</p>')

def error_403(request, exception=None):
    """Handle 403 Forbidden errors"""
    logger.warning(f"403 error: {request.path}")
    if request.path.startswith('/api/'):
        from django.http import JsonResponse
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    try:
        return render(request, 'errors/403.html', status=403)
    except:
        return HttpResponseForbidden('<h1>403 - Forbidden</h1><p>You don\'t have permission to access this page.</p>')

def error_404(request, exception=None):
    """Handle 404 Not Found errors"""
    logger.warning(f"404 error: {request.path}")
    
    # For API endpoints
    if request.path.startswith('/api/'):
        from django.http import JsonResponse
        return JsonResponse({'error': 'Not found'}, status=404)
    
    # For asset requests (images, css, js)
    if any(ext in request.path for ext in ['.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.ico']):
        return HttpResponseNotFound('<h1>404 - File Not Found</h1>')
    
    try:
        return render(request, 'errors/404.html', status=404)
    except:
        return HttpResponseNotFound('<h1>404 - Page Not Found</h1><p>The page you\'re looking for doesn\'t exist.</p>')

def error_500(request):
    """Handle 500 Server Error"""
    logger.error(f"500 error: {request.path}")
    
    # For API endpoints
    if request.path.startswith('/api/'):
        from django.http import JsonResponse
        return JsonResponse({'error': 'Internal server error'}, status=500)
    
    try:
        return render(request, 'errors/500.html', status=500)
    except:
        return HttpResponseServerError('<h1>500 - Server Error</h1><p>Something went wrong. Please try again later.</p>')

def error_503(request):
    """Handle 503 Service Unavailable"""
    logger.error(f"503 error: {request.path}")
    
    try:
        return render(request, 'errors/503.html', status=503)
    except:
        return HttpResponseServerError('<h1>503 - Service Unavailable</h1><p>Please try again later.</p>')
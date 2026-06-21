from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import SiteSettings
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
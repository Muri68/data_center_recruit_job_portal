from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import timedelta
from jobs.models import Job, JobApplication, JobCategory
from blog.models import BlogPost
from accounts.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from core.models import SiteSettings
from django.utils.text import slugify

def is_admin(user):
    return user.is_admin_user()

@login_required
@user_passes_test(is_admin, login_url='dashboard:redirect_dashboard')
def admin_dashboard(request):
    # Get date ranges
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)
    
    # Statistics
    total_jobs = Job.objects.count()
    published_jobs = Job.objects.filter(status='published').count()
    total_applications = JobApplication.objects.count()
    total_users = CustomUser.objects.filter(user_type='job_seeker').count()
    
    # Recent activity
    recent_applications = JobApplication.objects.select_related(
        'job', 'applicant'
    ).order_by('-applied_at')[:10]
    
    recent_jobs = Job.objects.filter(
        status='published'
    ).order_by('-posted_at')[:5]
    
    # Applications by status
    application_status = JobApplication.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Applications trend (last 30 days)
    applications_trend = []
    for i in range(30):
        date = today - timedelta(days=i)
        count = JobApplication.objects.filter(
            applied_at__date=date.date()
        ).count()
        applications_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    applications_trend.reverse()
    
    # Jobs by category
    jobs_by_category = JobCategory.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')[:10]
    
    # Top performing jobs
    top_jobs = Job.objects.filter(
        status='published'
    ).annotate(
        app_count=Count('applications')
    ).order_by('-app_count')[:10]
    
    # Recent users
    recent_users = CustomUser.objects.filter(
        user_type='job_seeker'
    ).order_by('-date_joined')[:10]
    
    # Application status distribution for chart
    status_distribution = {
        'pending': application_status.filter(status='pending').aggregate(count=Count('id'))['count'] or 0,
        'reviewed': application_status.filter(status='reviewed').aggregate(count=Count('id'))['count'] or 0,
        'shortlisted': application_status.filter(status='shortlisted').aggregate(count=Count('id'))['count'] or 0,
        'interviewed': application_status.filter(status='interviewed').aggregate(count=Count('id'))['count'] or 0,
        'offered': application_status.filter(status='offered').aggregate(count=Count('id'))['count'] or 0,
        'hired': application_status.filter(status='hired').aggregate(count=Count('id'))['count'] or 0,
        'rejected': application_status.filter(status='rejected').aggregate(count=Count('id'))['count'] or 0,
    }
    
    context = {
        'total_jobs': total_jobs,
        'published_jobs': published_jobs,
        'total_applications': total_applications,
        'total_users': total_users,
        'recent_applications': recent_applications,
        'recent_jobs': recent_jobs,
        'applications_trend': applications_trend,
        'jobs_by_category': jobs_by_category,
        'top_jobs': top_jobs,
        'recent_users': recent_users,
        'status_distribution': status_distribution,
        'page_title': 'Admin Dashboard',
    }
    return render(request, 'dashboard/admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    context = {
        'page_title': 'Admin Profile',
    }
    return render(request, 'dashboard/admin/profile.html', context)

@login_required
@user_passes_test(is_admin)
def admin_update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.location = request.POST.get('location', user.location)
        user.bio = request.POST.get('bio', user.bio)
        
        if request.FILES.get('profile_picture'):
            if user.profile_picture:
                user.profile_picture.delete(save=False)
            user.profile_picture = request.FILES['profile_picture']
        
        user.email_notifications = request.POST.get('email_notifications') == 'on'
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard:admin_profile')
    
    context = {
        'page_title': 'Update Admin Profile',
    }
    return render(request, 'dashboard/admin/update_profile.html', context)


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
@user_passes_test(is_admin)
def admin_change_password(request):
    """Custom change password view for admin"""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard:admin_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    context = {
        'form': form,
        'page_title': 'Change Password',
    }
    return render(request, 'dashboard/admin/change_password.html', context)

@login_required
@user_passes_test(is_admin)
def admin_applications(request):
    status_filter = request.GET.get('status', '')
    job_filter = request.GET.get('job', '')
    search_query = request.GET.get('q', '')
    
    applications = JobApplication.objects.select_related(
        'job', 'applicant'
    ).all()
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    if job_filter:
        applications = applications.filter(job_id=job_filter)
    
    if search_query:
        applications = applications.filter(
            Q(applicant__email__icontains=search_query) |
            Q(applicant__first_name__icontains=search_query) |
            Q(applicant__last_name__icontains=search_query) |
            Q(job__title__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)
    
    jobs = Job.objects.filter(status='published')
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
        'job_filter': job_filter,
        'search_query': search_query,
        'jobs': jobs,
        'page_title': 'Manage Applications',
    }
    return render(request, 'dashboard/admin/applications.html', context)

@login_required
@user_passes_test(is_admin)
def update_application_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        if new_status in dict(JobApplication.STATUS_CHOICES):
            old_status = application.status
            application.status = new_status
            application.admin_notes = admin_notes
            application.status_updated_at = timezone.now()
            application.save()
            
            # Send email notification to applicant
            if new_status != old_status:
                send_status_update_email(application, old_status, new_status)
            
            messages.success(request, f'Application status updated to {application.get_status_display()}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('dashboard:admin_application_detail', application_id=application_id)

@login_required
@user_passes_test(is_admin)
def admin_application_detail(request, application_id):
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'applicant'), 
        id=application_id
    )
    
    context = {
        'application': application,
        'page_title': f'Application - {application.applicant.get_full_name()}',
    }
    return render(request, 'dashboard/admin/application_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_jobs(request):
    jobs = Job.objects.all().order_by('-posted_at')
    
    # Filters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    
    if category_filter:
        jobs = jobs.filter(category_id=category_filter)
    
    # Pagination
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    
    categories = JobCategory.objects.all()
    
    context = {
        'jobs': jobs,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'categories': categories,
        'page_title': 'Manage Jobs',
    }
    return render(request, 'dashboard/admin/jobs.html', context)

@login_required
@user_passes_test(is_admin)
def create_job(request):
    if request.method == 'POST':
        # Process job creation form
        job = Job.objects.create(
            title=request.POST.get('title'),
            slug=slugify(request.POST.get('title')),
            category_id=request.POST.get('category'),
            company_name=request.POST.get('company_name'),
            location=request.POST.get('location'),
            job_type=request.POST.get('job_type'),
            experience_level=request.POST.get('experience_level'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            benefits=request.POST.get('benefits'),
            salary_min=request.POST.get('salary_min') or None,
            salary_max=request.POST.get('salary_max') or None,
            salary_currency=request.POST.get('salary_currency', 'USD'),
            is_salary_negotiable=request.POST.get('is_salary_negotiable') == 'on',
            vacancies=request.POST.get('vacancies', 1),
            application_deadline=request.POST.get('application_deadline') or None,
            status=request.POST.get('status', 'draft'),
            is_featured=request.POST.get('is_featured') == 'on',
            is_remote=request.POST.get('is_remote') == 'on',
            posted_by=request.user,
        )
        
        # Handle company logo
        if request.FILES.get('company_logo'):
            job.company_logo = request.FILES['company_logo']
            job.save()
        
        # Add skills
        skills = request.POST.get('skills_required', '')
        if skills:
            job.skills_required.add(*[s.strip() for s in skills.split(',')])
        
        messages.success(request, 'Job created successfully!')
        return redirect('dashboard:admin_jobs')
    
    categories = JobCategory.objects.all()
    context = {
        'categories': categories,
        'page_title': 'Create Job',
    }
    return render(request, 'dashboard/admin/create_job.html', context)

@login_required
@user_passes_test(is_admin)
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.category_id = request.POST.get('category')
        job.company_name = request.POST.get('company_name')
        job.location = request.POST.get('location')
        job.job_type = request.POST.get('job_type')
        job.experience_level = request.POST.get('experience_level')
        job.description = request.POST.get('description')
        job.requirements = request.POST.get('requirements')
        job.benefits = request.POST.get('benefits')
        job.salary_min = request.POST.get('salary_min') or None
        job.salary_max = request.POST.get('salary_max') or None
        job.salary_currency = request.POST.get('salary_currency', 'USD')
        job.is_salary_negotiable = request.POST.get('is_salary_negotiable') == 'on'
        job.vacancies = request.POST.get('vacancies', 1)
        job.application_deadline = request.POST.get('application_deadline') or None
        job.status = request.POST.get('status', 'draft')
        job.is_featured = request.POST.get('is_featured') == 'on'
        job.is_remote = request.POST.get('is_remote') == 'on'
        
        if request.FILES.get('company_logo'):
            job.company_logo = request.FILES['company_logo']
        
        job.save()
        
        # Update skills
        job.skills_required.clear()
        skills = request.POST.get('skills_required', '')
        if skills:
            job.skills_required.add(*[s.strip() for s in skills.split(',')])
        
        messages.success(request, 'Job updated successfully!')
        return redirect('dashboard:admin_jobs')
    
    categories = JobCategory.objects.all()
    context = {
        'job': job,
        'categories': categories,
        'page_title': f'Edit Job - {job.title}',
    }
    return render(request, 'dashboard/admin/edit_job.html', context)

@login_required
@user_passes_test(is_admin)
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        job_title = job.title
        job.delete()
        messages.success(request, f'Job "{job_title}" deleted successfully!')
        return redirect('dashboard:admin_jobs')
    
    return render(request, 'dashboard/admin/delete_job.html', {'job': job})

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    users = CustomUser.objects.filter(user_type='admin').order_by('-date_joined')
    
    search_query = request.GET.get('q', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'search_query': search_query,
        'page_title': 'Manage Users',
    }
    return render(request, 'dashboard/admin/users.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    applications = JobApplication.objects.filter(
        applicant=user
    ).select_related('job').order_by('-applied_at')
    
    context = {
        'user_detail': user,
        'applications': applications,
        'page_title': f'User - {user.get_full_name()}',
    }
    return render(request, 'dashboard/admin/user_detail.html', context)

def send_status_update_email(application, old_status, new_status):
    """Send email when application status changes"""
    subject = f"Application Status Update - {application.job.title}"
    
    status_messages = {
        'reviewed': 'Your application has been reviewed by the hiring team.',
        'shortlisted': 'Congratulations! You have been shortlisted for the next stage.',
        'interviewed': 'You have been marked as interviewed.',
        'offered': 'Congratulations! You have been offered the position.',
        'hired': 'Congratulations! You have been hired for this position.',
        'rejected': 'Thank you for your interest. Unfortunately, we have decided to move forward with other candidates.',
    }
    
    status_message = status_messages.get(new_status, f'Your application status has been updated to {application.get_status_display()}.')
    
    message = f"""
    Dear {application.applicant.get_full_name()},
    
    Your application for the position of {application.job.title} at {application.job.company_name} has been updated.
    
    New Status: {application.get_status_display()}
    
    {status_message}
    
    You can view the details of your application by logging into your dashboard.
    
    Best regards,
    {SiteSettings.objects.first().site_name} Team
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.applicant.email],
            fail_silently=True,
        )
    except:
        pass

@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    """Generate various reports"""
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    
    # Applications over time
    daily_applications = JobApplication.objects.filter(
        applied_at__gte=thirty_days_ago
    ).extra(
        select={'date': 'date(applied_at)'}
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    # Jobs by category
    category_stats = JobCategory.objects.annotate(
        total_jobs=Count('jobs'),
        active_jobs=Count('jobs', filter=Q(jobs__status='published')),
        total_applications=Count('jobs__applications')
    )
    
    # Hiring funnel
    funnel = {
        'applied': JobApplication.objects.count(),
        'reviewed': JobApplication.objects.filter(status='reviewed').count(),
        'shortlisted': JobApplication.objects.filter(status='shortlisted').count(),
        'interviewed': JobApplication.objects.filter(status='interviewed').count(),
        'offered': JobApplication.objects.filter(status='offered').count(),
        'hired': JobApplication.objects.filter(status='hired').count(),
        'rejected': JobApplication.objects.filter(status='rejected').count(),
    }
    
    context = {
        'daily_applications': daily_applications,
        'category_stats': category_stats,
        'funnel': funnel,
        'page_title': 'Reports & Analytics',
    }
    return render(request, 'dashboard/admin/reports.html', context)



@login_required
@user_passes_test(is_admin)
def site_settings(request):
    """Manage site settings"""
    settings_obj = SiteSettings.objects.first()
    
    if not settings_obj:
        settings_obj = SiteSettings.objects.create(
            site_name='JobPortal Pro',
            email='admin@jobportal.com'
        )
    
    if request.method == 'POST':
        # Update General
        settings_obj.site_name = request.POST.get('site_name', settings_obj.site_name)
        settings_obj.tagline = request.POST.get('tagline', settings_obj.tagline)
        
        # Update Branding
        if request.FILES.get('logo'):
            if settings_obj.logo:
                settings_obj.logo.delete(save=False)
            settings_obj.logo = request.FILES['logo']
        
        if request.FILES.get('favicon'):
            if settings_obj.favicon:
                settings_obj.favicon.delete(save=False)
            settings_obj.favicon = request.FILES['favicon']
        
        settings_obj.primary_color = request.POST.get('primary_color', settings_obj.primary_color)
        settings_obj.secondary_color = request.POST.get('secondary_color', settings_obj.secondary_color)
        
        # Update About
        settings_obj.about_title = request.POST.get('about_title', settings_obj.about_title)
        settings_obj.about_description = request.POST.get('about_description', settings_obj.about_description)
        settings_obj.mission = request.POST.get('mission', settings_obj.mission)
        settings_obj.vision = request.POST.get('vision', settings_obj.vision)
        
        # Update Contact
        settings_obj.email = request.POST.get('email', settings_obj.email)
        settings_obj.phone = request.POST.get('phone', settings_obj.phone)
        settings_obj.address = request.POST.get('address', settings_obj.address)
        settings_obj.google_map_embed = request.POST.get('google_map_embed', settings_obj.google_map_embed)
        
        # Update Social
        settings_obj.facebook = request.POST.get('facebook', settings_obj.facebook)
        settings_obj.twitter = request.POST.get('twitter', settings_obj.twitter)
        settings_obj.linkedin = request.POST.get('linkedin', settings_obj.linkedin)
        settings_obj.instagram = request.POST.get('instagram', settings_obj.instagram)
        settings_obj.youtube = request.POST.get('youtube', settings_obj.youtube)
        
        # Update SEO
        settings_obj.meta_description = request.POST.get('meta_description', settings_obj.meta_description)
        settings_obj.meta_keywords = request.POST.get('meta_keywords', settings_obj.meta_keywords)
        
        # Update Footer
        settings_obj.footer_text = request.POST.get('footer_text', settings_obj.footer_text)
        settings_obj.copyright_text = request.POST.get('copyright_text', settings_obj.copyright_text)
        
        # Update Advanced
        settings_obj.custom_css = request.POST.get('custom_css', settings_obj.custom_css)
        settings_obj.custom_js = request.POST.get('custom_js', settings_obj.custom_js)
        settings_obj.google_analytics = request.POST.get('google_analytics', settings_obj.google_analytics)
        
        settings_obj.save()
        messages.success(request, 'Site settings updated successfully!')
        return redirect('dashboard:site_settings')
    
    context = {
        'site_settings': settings_obj,
        'page_title': 'Site Settings',
    }
    return render(request, 'dashboard/admin/site_settings.html', context)




from core.models import FAQ, WhyChooseUs
import json
from django.http import JsonResponse

@login_required
@user_passes_test(is_admin)
def manage_faqs(request):
    faqs = FAQ.objects.all().order_by('order')
    context = {
        'faqs': faqs,
        'page_title': 'Manage FAQs',
    }
    return render(request, 'dashboard/admin/manage_faqs.html', context)

@login_required
@user_passes_test(is_admin)
def add_faq(request):
    if request.method == 'POST':
        try:
            FAQ.objects.create(
                question=request.POST.get('question'),
                answer=request.POST.get('answer'),
                order=request.POST.get('order', 0),
                is_active=request.POST.get('is_active') == 'on'
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@user_passes_test(is_admin)
def edit_faq(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    if request.method == 'POST':
        try:
            faq.question = request.POST.get('question', faq.question)
            faq.answer = request.POST.get('answer', faq.answer)
            faq.order = request.POST.get('order', faq.order)
            faq.is_active = request.POST.get('is_active') == 'on'
            faq.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@user_passes_test(is_admin)
def delete_faq(request, faq_id):
    faq = get_object_or_404(FAQ, id=faq_id)
    faq.delete()
    messages.success(request, 'FAQ deleted successfully!')
    return redirect('dashboard:admin_faqs')

# Similar functions for WhyChooseUs...
@login_required
@user_passes_test(is_admin)
def manage_why_choose_us(request):
    features = WhyChooseUs.objects.all().order_by('order')
    context = {
        'features': features,
        'page_title': 'Manage Why Choose Us',
    }
    return render(request, 'dashboard/admin/manage_why_choose_us.html', context)

@login_required
@user_passes_test(is_admin)
def add_why_choose_us(request):
    if request.method == 'POST':
        try:
            WhyChooseUs.objects.create(
                icon=request.POST.get('icon', 'fas fa-star'),
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                order=request.POST.get('order', 0),
                is_active=request.POST.get('is_active') == 'on'
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@user_passes_test(is_admin)
def edit_why_choose_us(request, feature_id):
    feature = get_object_or_404(WhyChooseUs, id=feature_id)
    if request.method == 'POST':
        try:
            feature.icon = request.POST.get('icon', feature.icon)
            feature.title = request.POST.get('title', feature.title)
            feature.description = request.POST.get('description', feature.description)
            feature.order = request.POST.get('order', feature.order)
            feature.is_active = request.POST.get('is_active') == 'on'
            feature.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@user_passes_test(is_admin)
def delete_why_choose_us(request, feature_id):
    feature = get_object_or_404(WhyChooseUs, id=feature_id)
    feature.delete()
    messages.success(request, 'Feature deleted successfully!')
    return redirect('dashboard:admin_why_choose_us')



# Add these views to your views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import redirect
from core.models import LegalPage


@login_required
@user_passes_test(is_admin)
def admin_legal_pages(request):
    """Admin view to list all legal pages"""
    legal_pages = LegalPage.objects.all().order_by('page_type')
    
    context = {
        'legal_pages': legal_pages,
        'page_title': 'Legal Pages Management',
    }
    return render(request, 'dashboard/admin/legal_pages.html', context)


@login_required
@user_passes_test(is_admin)
def admin_legal_page_edit(request, page_id=None):
    """Admin view to create/edit legal page"""
    if page_id:
        page = get_object_or_404(LegalPage, id=page_id)
    else:
        page = None
    
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        page_type = request.POST.get('page_type')
        content = request.POST.get('content')
        is_active = request.POST.get('is_active') == 'on'
        meta_description = request.POST.get('meta_description', '')
        meta_keywords = request.POST.get('meta_keywords', '')
        
        if page:
            # Update existing page
            page.title = title
            page.slug = slug
            page.page_type = page_type
            page.content = content
            page.is_active = is_active
            page.meta_description = meta_description
            page.meta_keywords = meta_keywords
            page.save()
            messages.success(request, f'"{title}" updated successfully!')
        else:
            # Create new page
            page = LegalPage.objects.create(
                title=title,
                slug=slug,
                page_type=page_type,
                content=content,
                is_active=is_active,
                meta_description=meta_description,
                meta_keywords=meta_keywords
            )
            messages.success(request, f'"{title}" created successfully!')
        
        return redirect('dashboard:admin_legal_pages')
    
    context = {
        'page': page,
        'page_types': LegalPage.PAGE_TYPES,
        'page_title': 'Edit Legal Page' if page else 'Create Legal Page',
    }
    return render(request, 'dashboard/admin/legal_page_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_legal_page_delete(request, page_id):
    """Admin view to delete legal page"""
    page = get_object_or_404(LegalPage, id=page_id)
    
    if request.method == 'POST':
        title = page.title
        page.delete()
        messages.success(request, f'"{title}" deleted successfully!')
        return redirect('dashboard:admin_legal_pages')
    
    context = {
        'page': page,
        'page_title': 'Delete Legal Page',
    }
    return render(request, 'dashboard/admin/legal_page_confirm_delete.html', context)




from blog.models import BlogPost, BlogCategory, BlogComment
from django.utils.text import slugify

@login_required
@user_passes_test(is_admin)
def admin_blog_posts(request):
    """Manage all blog posts"""
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('q', '')
    
    posts = BlogPost.objects.select_related('category', 'author').all()
    
    if status_filter:
        posts = posts.filter(status=status_filter)
    
    if category_filter:
        posts = posts.filter(category_id=category_filter)
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(posts.order_by('-created_at'), 12)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    categories = BlogCategory.objects.all()
    
    # Statistics
    total_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(status='published').count()
    draft_posts = BlogPost.objects.filter(status='draft').count()
    total_comments = BlogComment.objects.count()
    
    context = {
        'posts': posts,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_comments': total_comments,
        'page_title': 'Manage Blog Posts',
    }
    return render(request, 'dashboard/admin/blog/posts.html', context)


@login_required
@user_passes_test(is_admin)
def admin_create_blog_post(request):
    """Create a new blog post"""
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = slugify(title)
        
        # Ensure unique slug
        original_slug = slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        post = BlogPost.objects.create(
            title=title,
            slug=slug,
            category_id=request.POST.get('category'),
            excerpt=request.POST.get('excerpt'),
            content=request.POST.get('content'),
            author=request.user,
            status=request.POST.get('status', 'draft'),
        )
        
        if request.FILES.get('featured_image'):
            post.featured_image = request.FILES['featured_image']
            post.save()
        
        # Handle tags
        tags = request.POST.get('tags', '')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            post.tags.add(*tag_list)
        
        messages.success(request, f'Blog post "{title}" created successfully!')
        return redirect('dashboard:admin_blog_posts')
    
    categories = BlogCategory.objects.all()
    context = {
        'categories': categories,
        'page_title': 'Create Blog Post',
    }
    return render(request, 'dashboard/admin/blog/create_post.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_blog_post(request, post_id):
    """Edit a blog post"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        post.title = request.POST.get('title', post.title)
        post.category_id = request.POST.get('category', post.category_id)
        post.excerpt = request.POST.get('excerpt', post.excerpt)
        post.content = request.POST.get('content', post.content)
        post.status = request.POST.get('status', post.status)
        
        if request.FILES.get('featured_image'):
            if post.featured_image:
                post.featured_image.delete(save=False)
            post.featured_image = request.FILES['featured_image']
        
        post.save()
        
        # Update tags
        post.tags.clear()
        tags = request.POST.get('tags', '')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            post.tags.add(*tag_list)
        
        messages.success(request, f'Blog post "{post.title}" updated successfully!')
        return redirect('dashboard:admin_blog_posts')
    
    categories = BlogCategory.objects.all()
    context = {
        'post': post,
        'categories': categories,
        'page_title': f'Edit - {post.title}',
    }
    return render(request, 'dashboard/admin/blog/edit_post.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_blog_post(request, post_id):
    """Delete a blog post"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Blog post "{post_title}" deleted successfully!')
        return redirect('dashboard:admin_blog_posts')
    
    context = {
        'post': post,
        'page_title': f'Delete - {post.title}',
    }
    return render(request, 'dashboard/admin/blog/delete_post.html', context)


@login_required
@user_passes_test(is_admin)
def admin_blog_categories(request):
    """Manage blog categories"""
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = slugify(name)
        description = request.POST.get('description', '')
        
        if BlogCategory.objects.filter(slug=slug).exists():
            messages.error(request, 'A category with this name already exists.')
        else:
            BlogCategory.objects.create(
                name=name,
                slug=slug,
                description=description
            )
            messages.success(request, f'Category "{name}" created successfully!')
        return redirect('dashboard:admin_blog_categories')
    
    categories = BlogCategory.objects.annotate(
        post_count=Count('posts')
    ).all()
    
    context = {
        'categories': categories,
        'page_title': 'Manage Blog Categories',
    }
    return render(request, 'dashboard/admin/blog/categories.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_blog_category(request, category_id):
    """Edit a blog category"""
    category = get_object_or_404(BlogCategory, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name', category.name)
        category.description = request.POST.get('description', category.description)
        category.save()
        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('dashboard:admin_blog_categories')
    
    return redirect('dashboard:admin_blog_categories')


@login_required
@user_passes_test(is_admin)
def admin_delete_blog_category(request, category_id):
    """Delete a blog category"""
    category = get_object_or_404(BlogCategory, id=category_id)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('dashboard:admin_blog_categories')
    
    return redirect('dashboard:admin_blog_categories')


@login_required
@user_passes_test(is_admin)
def admin_blog_comments(request):
    """Manage blog comments"""
    status_filter = request.GET.get('status', '')
    
    comments = BlogComment.objects.select_related('post', 'user').all()
    
    if status_filter == 'approved':
        comments = comments.filter(is_approved=True)
    elif status_filter == 'pending':
        comments = comments.filter(is_approved=False)
    
    # Pagination
    paginator = Paginator(comments.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)
    
    context = {
        'comments': comments,
        'status_filter': status_filter,
        'page_title': 'Manage Comments',
    }
    return render(request, 'dashboard/admin/blog/comments.html', context)


@login_required
@user_passes_test(is_admin)
def admin_toggle_comment(request, comment_id):
    """Approve/Unapprove a comment"""
    comment = get_object_or_404(BlogComment, id=comment_id)
    comment.is_approved = not comment.is_approved
    comment.save()
    
    status = 'approved' if comment.is_approved else 'unapproved'
    messages.success(request, f'Comment {status} successfully!')
    return redirect('dashboard:admin_blog_comments')


@login_required
@user_passes_test(is_admin)
def admin_delete_blog_comment(request, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(BlogComment, id=comment_id)
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('dashboard:admin_blog_comments')

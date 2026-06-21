from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from core.models import SiteSettings
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from jobs.models import Job, JobApplication, ApplicationTimeline
from accounts.models import CustomUser
from django.http import JsonResponse


@login_required
def redirect_dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    if request.user.is_admin_user():
        return redirect('dashboard:admin_dashboard')
    return redirect('dashboard:job_seeker_dashboard')


@login_required
def job_seeker_dashboard(request):
    if not request.user.is_job_seeker():
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    # Get statistics
    total_applications = JobApplication.objects.filter(applicant=request.user).count()
    active_applications = JobApplication.objects.filter(
        applicant=request.user, 
        status__in=['pending', 'reviewed', 'shortlisted', 'interviewed']
    ).count()
    shortlisted = JobApplication.objects.filter(
        applicant=request.user, 
        status='shortlisted'
    ).count()
    rejected = JobApplication.objects.filter(
        applicant=request.user, 
        status='rejected'
    ).count()
    hired = JobApplication.objects.filter(
        applicant=request.user, 
        status='hired'
    ).count()
    
    # Recent applications with timeline
    recent_applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__category').prefetch_related('timeline').order_by('-applied_at')[:5]
    
    # Recommended jobs based on skills
    if request.user.skills:
        skills_list = [skill.strip() for skill in request.user.skills.split(',')]
        recommended_jobs = Job.objects.filter(
            status='published',
            skills_required__name__in=skills_list
        ).exclude(
            applications__applicant=request.user
        ).distinct()[:5]
    else:
        recommended_jobs = Job.objects.filter(
            status='published'
        ).exclude(
            applications__applicant=request.user
        ).order_by('-posted_at')[:5]
    
    # Get jobs with upcoming deadlines
    upcoming_deadlines = JobApplication.objects.filter(
        applicant=request.user,
        status__in=['pending', 'reviewed', 'shortlisted'],
        job__application_deadline__isnull=False,
        job__application_deadline__gte=timezone.now()
    ).select_related('job').order_by('job__application_deadline')[:3]
    
    context = {
        'total_applications': total_applications,
        'active_applications': active_applications,
        'shortlisted': shortlisted,
        'rejected': rejected,
        'hired': hired,
        'recent_applications': recent_applications,
        'recommended_jobs': recommended_jobs,
        'upcoming_deadlines': upcoming_deadlines,
        'page_title': 'Job Seeker Dashboard',
    }
    return render(request, 'dashboard/job_seeker_dashboard.html', context)


@login_required
def my_applications(request):
    if not request.user.is_job_seeker():
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-applied_at')
    
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__category').prefetch_related('timeline')
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(job__company_name__icontains=search_query)
        )
    
    # Sorting
    valid_sorts = ['-applied_at', 'applied_at', 'status', '-status', 'job__title', '-job__title']
    if sort_by in valid_sorts:
        applications = applications.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    applications = paginator.get_page(page_number)
    
    # Get status counts for sidebar
    status_counts = {
        'all': JobApplication.objects.filter(applicant=request.user).count(),
        'pending': JobApplication.objects.filter(applicant=request.user, status='pending').count(),
        'reviewed': JobApplication.objects.filter(applicant=request.user, status='reviewed').count(),
        'shortlisted': JobApplication.objects.filter(applicant=request.user, status='shortlisted').count(),
        'interviewed': JobApplication.objects.filter(applicant=request.user, status='interviewed').count(),
        'offered': JobApplication.objects.filter(applicant=request.user, status='offered').count(),
        'hired': JobApplication.objects.filter(applicant=request.user, status='hired').count(),
        'rejected': JobApplication.objects.filter(applicant=request.user, status='rejected').count(),
        'withdrawn': JobApplication.objects.filter(applicant=request.user, status='withdrawn').count(),
    }
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'status_counts': status_counts,
        'page_title': 'My Applications',
    }
    return render(request, 'dashboard/my_applications.html', context)


@login_required
def apply_job(request, job_slug):
    if not request.user.is_job_seeker():
        messages.error(request, 'Only job seekers can apply for jobs.')
        return redirect('jobs:job_detail', slug=job_slug)
    
    job = get_object_or_404(Job, slug=job_slug, status='published')
    
    # Check if already applied
    existing_application = JobApplication.objects.filter(
        job=job, 
        applicant=request.user
    ).first()
    
    if existing_application:
        if existing_application.status == 'withdrawn':
            messages.info(request, 'You previously withdrew your application. You can reapply below.')
        elif existing_application.status == 'rejected':
            messages.info(request, 'Your previous application was not selected. You can try applying again.')
        else:
            messages.warning(request, 'You have already applied for this job.')
            return redirect('dashboard:application_detail', application_id=existing_application.id)
    
    # Check if deadline has passed
    if job.application_deadline and timezone.now() > job.application_deadline:
        messages.error(request, 'The application deadline for this job has passed.')
        return redirect('jobs:job_detail', slug=job_slug)
    
    # Check if job is still accepting applications
    if job.status != 'published':
        messages.error(request, 'This job is no longer accepting applications.')
        return redirect('jobs:job_detail', slug=job_slug)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        resume = request.FILES.get('resume')
        notes = request.POST.get('notes', '')
        
        # Validate required fields
        if not cover_letter or len(cover_letter.strip()) < 50:
            messages.error(request, 'Please write a cover letter of at least 50 characters.')
            return render(request, 'dashboard/apply_job.html', {'job': job})
        
        if not resume and not request.user.resume:
            messages.error(request, 'Please upload your resume or update your profile with a resume.')
            return render(request, 'dashboard/apply_job.html', {'job': job})
        
        # Use uploaded resume or profile resume
        if not resume:
            resume = request.user.resume
        
        # Delete old withdrawn/rejected application if exists
        if existing_application:
            existing_application.delete()
        
        # Create new application
        application = JobApplication.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter,
            resume=resume,
            notes=notes,
            status='pending',
            status_updated_at=timezone.now()
        )
        
        # Create initial timeline entry
        ApplicationTimeline.objects.create(
            application=application,
            status='pending',
            title='Application Submitted',
            description=f'Your application for {job.title} at {job.company_name} has been submitted successfully. The employer will review your application and get back to you.',
            created_by=request.user,
            is_system_generated=True
        )
        
        # Update job applications count
        job.applications_count = job.applications.filter(status__in=['pending', 'reviewed', 'shortlisted', 'interviewed', 'offered', 'hired']).count()
        job.save()
        
        # Send confirmation email
        send_application_confirmation(application)
        
        messages.success(request, 'Your application has been submitted successfully!')
        return redirect('dashboard:application_detail', application_id=application.id)
    
    context = {
        'job': job,
        'existing_application': existing_application,
        'page_title': f'Apply for {job.title}',
    }
    return render(request, 'dashboard/apply_job.html', context)


@login_required
def application_detail(request, application_id):
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'job__category', 'applicant').prefetch_related('timeline'), 
        id=application_id, 
        applicant=request.user
    )
    
    # Get complete application timeline ordered by most recent first
    timeline = application.timeline.all().order_by('-created_at')
    
    # Get similar jobs for recommendations
    similar_jobs = Job.objects.filter(
        status='published',
        category=application.job.category
    ).exclude(
        Q(id=application.job.id) |
        Q(applications__applicant=request.user)
    ).order_by('-posted_at')[:3]
    
    # Get application age
    days_since_applied = (timezone.now() - application.applied_at).days
    
    context = {
        'application': application,
        'timeline': timeline,
        'similar_jobs': similar_jobs,
        'days_since_applied': days_since_applied,
        'page_title': f'Application - {application.job.title}',
    }
    return render(request, 'dashboard/application_detail.html', context)


@login_required
def withdraw_application(request, application_id):
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'applicant'), 
        id=application_id, 
        applicant=request.user
    )
    
    # Check if application can be withdrawn
    can_withdraw = application.status in ['pending', 'reviewed', 'shortlisted', 'interviewed', 'offered']
    
    if request.method == 'POST':
        if not can_withdraw:
            messages.error(request, 'This application cannot be withdrawn because it has already been processed.')
            return redirect('dashboard:application_detail', application_id=application_id)
        
        # Store old status for reference
        old_status = application.status
        withdraw_reason = request.POST.get('withdraw_reason', '')
        other_reason = request.POST.get('other_reason', '')
        
        # Update application status
        application.status = 'withdrawn'
        application.status_updated_at = timezone.now()
        application.save()
        
        # Build timeline description
        reason_text = ""
        if withdraw_reason == 'other' and other_reason:
            reason_text = f"\nReason: {other_reason}"
        elif withdraw_reason:
            reason_display = {
                'accepted_another': 'Accepted another job offer',
                'salary_expectations': 'Salary expectations not met',
                'location': 'Location not suitable',
                'role_change': 'Changed mind about the role',
                'company_research': 'After researching the company',
                'personal_reasons': 'Personal reasons',
            }
            reason_text = f"\nReason: {reason_display.get(withdraw_reason, withdraw_reason)}"
        
        # Create timeline entry for withdrawal
        ApplicationTimeline.objects.create(
            application=application,
            status='withdrawn',
            title='Application Withdrawn',
            description=f'You withdrew your application for the {application.job.title} position at {application.job.company_name}.{reason_text}',
            created_by=request.user,
            is_system_generated=False
        )
        
        # Update job applications count
        job = application.job
        job.applications_count = job.applications.filter(status__in=['pending', 'reviewed', 'shortlisted', 'interviewed', 'offered', 'hired']).count()
        job.save()
        
        # Send withdrawal confirmation email
        send_withdrawal_confirmation(application, withdraw_reason)
        
        messages.success(request, f'Your application for {application.job.title} has been withdrawn successfully.')
        return redirect('dashboard:my_applications')
    
    # GET request - show confirmation page with warning
    context = {
        'application': application,
        'can_withdraw': can_withdraw,
        'page_title': 'Withdraw Application',
    }
    return render(request, 'dashboard/withdraw_application.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        
        # Update basic info
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.location = request.POST.get('location', user.location)
        user.bio = request.POST.get('bio', user.bio)
        user.skills = request.POST.get('skills', user.skills)
        user.linkedin_profile = request.POST.get('linkedin_profile', user.linkedin_profile)
        user.github_profile = request.POST.get('github_profile', user.github_profile)
        user.portfolio_website = request.POST.get('portfolio_website', user.portfolio_website)
        
        # Handle profile picture
        if request.FILES.get('profile_picture'):
            # Delete old profile picture if exists
            if user.profile_picture:
                user.profile_picture.delete(save=False)
            user.profile_picture = request.FILES['profile_picture']
        
        # Handle resume
        if request.FILES.get('resume'):
            # Delete old resume if exists
            if user.resume:
                user.resume.delete(save=False)
            user.resume = request.FILES['resume']
        
        # Notification preferences
        user.email_notifications = request.POST.get('email_notifications') == 'on'
        user.job_alerts = request.POST.get('job_alerts') == 'on'
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard:profile')
    
    context = {
        'page_title': 'Update Profile',
    }
    return render(request, 'dashboard/update_profile.html', context)


@login_required
def profile(request):
    # Get profile completion percentage
    user = request.user
    profile_completion = user.get_profile_completion()
    
    # Get application statistics
    application_stats = {
        'total': JobApplication.objects.filter(applicant=user).count(),
        'active': JobApplication.objects.filter(applicant=user, status__in=['pending', 'reviewed', 'shortlisted', 'interviewed']).count(),
        'successful': JobApplication.objects.filter(applicant=user, status__in=['offered', 'hired']).count(),
    }
    
    context = {
        'page_title': 'My Profile',
        'profile_completion': profile_completion,
        'application_stats': application_stats,
    }
    return render(request, 'dashboard/profile.html', context)


def send_application_confirmation(application):
    """Send email confirmation for job application"""
    try:
        site_settings = SiteSettings.objects.first()
        site_name = site_settings.site_name if site_settings else 'JobPortal Pro'
        
        subject = f"Application Received - {application.job.title}"
        message = f"""
Dear {application.applicant.get_full_name()},

Thank you for applying for the position of {application.job.title} at {application.job.company_name}.

Your application has been received and is being reviewed. We will notify you of any updates regarding your application status.

Job Details:
- Position: {application.job.title}
- Company: {application.job.company_name}
- Location: {application.job.location}
- Job Type: {application.job.get_job_type_display()}
- Application Date: {application.applied_at.strftime('%B %d, %Y')}
- Application ID: #{application.id}

What's Next?
1. The employer will review your application
2. If shortlisted, you'll receive an interview invitation
3. Track your application status on your dashboard

You can track your application status by logging into your dashboard:
http://127.0.0.1:8000/dashboard/applications/

Best regards,
{site_name} Team
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.applicant.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")


def send_withdrawal_confirmation(application, reason=''):
    """Send confirmation email when application is withdrawn"""
    try:
        site_settings = SiteSettings.objects.first()
        site_name = site_settings.site_name if site_settings else 'JobPortal Pro'
        
        reason_text = ""
        if reason:
            reason_display = {
                'accepted_another': 'Accepted another job offer',
                'salary_expectations': 'Salary expectations not met',
                'location': 'Location not suitable',
                'role_change': 'Changed mind about the role',
                'company_research': 'After researching the company',
                'personal_reasons': 'Personal reasons',
            }
            reason_text = f"\nReason for withdrawal: {reason_display.get(reason, reason)}"
        
        subject = f"Application Withdrawn - {application.job.title}"
        message = f"""
Dear {application.applicant.get_full_name()},

Your application for the position of {application.job.title} at {application.job.company_name} has been withdrawn as requested.{reason_text}

Application Details:
- Position: {application.job.title}
- Company: {application.job.company_name}
- Application ID: #{application.id}
- Withdrawn On: {timezone.now().strftime('%B %d, %Y')}

If you wish to reapply for this position or explore other opportunities, please visit our job portal:
http://127.0.0.1:8000/jobs/

We wish you the best in your career search!

Best regards,
{site_name} Team
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[application.applicant.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send withdrawal email: {e}")
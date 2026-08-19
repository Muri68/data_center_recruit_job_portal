from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job, JobCategory

def job_list(request):
    jobs = Job.objects.filter(status='published')
    
    # Filters
    search_query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    category_slug = request.GET.get('category', '')
    job_type = request.GET.get('job_type', '')
    experience_level = request.GET.get('experience_level', '')
    
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(skills_required__name__icontains=search_query)
        ).distinct()
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if category_slug:
        jobs = jobs.filter(category__slug=category_slug)
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)
    
    # Sorting
    sort_by = request.GET.get('sort', '-posted_at')
    if sort_by in ['-posted_at', 'posted_at', 'title', '-title', 'company_name', '-company_name']:
        jobs = jobs.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(jobs, 12)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    
    # Get filter options
    categories = JobCategory.objects.all()
    
    context = {
        'jobs': jobs,
        'categories': categories,
        'search_query': search_query,
        'location': location,
        'category_slug': category_slug,
        'job_type': job_type,
        'experience_level': experience_level,
        'sort_by': sort_by,
        'page_title': 'Job Listings',
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug, status='published')
    
    # Increment view count
    job.views_count += 1
    job.save()
    
    # Related jobs
    related_jobs = Job.objects.filter(
        Q(category=job.category) | Q(job_type=job.job_type),
        status='published'
    ).exclude(id=job.id)[:5]
    
    # Check if user has applied
    has_applied = False
    if request.user.is_authenticated and request.user.is_job_seeker():
        has_applied = job.applications.filter(applicant=request.user).exists()
    
    context = {
        'job': job,
        'related_jobs': related_jobs,
        'has_applied': has_applied,
        'page_title': job.title,
    }
    return render(request, 'jobs/job_detail.html', context)


def job_categories(request):
    categories = JobCategory.objects.all()
    
    # Job statistics
    total_jobs = Job.objects.filter(status='published').count()
    total_companies = Job.objects.filter(status='published').values('company_name').distinct().count()
    
    context = {
        'categories': categories,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'page_title': 'Job Categories',
    }
    return render(request, 'jobs/categories.html', context)
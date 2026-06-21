from django.db import models
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager

class JobCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    
    class Meta:
        verbose_name_plural = 'Job Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Job(models.Model):
    JOB_TYPE_CHOICES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
        ('freelance', 'Freelance'),
    )
    
    EXPERIENCE_LEVEL_CHOICES = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead/Manager'),
        ('executive', 'Executive'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='jobs')
    
    company_name = models.CharField(max_length=200)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    company_website = models.URLField(blank=True)
    
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)
    
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    is_salary_negotiable = models.BooleanField(default=False)
    
    description = CKEditor5Field(config_name='extends', blank=True, null=True)
    requirements = CKEditor5Field(config_name='extends', blank=True, null=True)
    benefits = CKEditor5Field(config_name='extends', blank=True, null=True)
    
    skills_required = TaggableManager(help_text="Required skills for this job")
    
    vacancies = models.PositiveIntegerField(default=1)
    application_deadline = models.DateTimeField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    is_featured = models.BooleanField(default=False)
    is_remote = models.BooleanField(default=False)
    
    posted_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['status', 'posted_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['location', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    def is_active(self):
        if self.application_deadline:
            return self.status == 'published' and timezone.now() <= self.application_deadline
        return self.status == 'published'
    
    def get_salary_range(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        elif self.salary_min:
            return f"From {self.salary_currency} {self.salary_min:,.0f}"
        elif self.salary_max:
            return f"Up to {self.salary_currency} {self.salary_max:,.0f}"
        return "Negotiable"

class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('interviewed', 'Interviewed'),
        ('offered', 'Offered'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='applications')
    
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='applications/resumes/')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'applicant']
    
    def __str__(self):
        return f"{self.applicant.email} - {self.job.title}"
    
    def get_status_color(self):
        status_colors = {
            'pending': 'warning',
            'reviewed': 'info',
            'shortlisted': 'primary',
            'interviewed': 'secondary',
            'offered': 'success',
            'hired': 'success',
            'rejected': 'danger',
            'withdrawn': 'dark text-white',
        }
        return status_colors.get(self.status, 'secondary')
    
    
    
class ApplicationTimeline(models.Model):
    """Track all status changes and events for an application"""
    
    STATUS_CHOICES = JobApplication.STATUS_CHOICES
    
    application = models.ForeignKey(
        JobApplication, 
        on_delete=models.CASCADE, 
        related_name='timeline'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        'accounts.CustomUser', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='timeline_entries'
    )
    is_system_generated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application Timeline'
        verbose_name_plural = 'Application Timelines'
    
    def __str__(self):
        return f"{self.application.id} - {self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_status_icon(self):
        """Return appropriate icon based on status"""
        icons = {
            'pending': 'fa-clock',
            'reviewed': 'fa-search',
            'shortlisted': 'fa-star',
            'interviewed': 'fa-comments',
            'offered': 'fa-check-circle',
            'hired': 'fa-trophy',
            'rejected': 'fa-times-circle',
            'withdrawn': 'fa-undo',
        }
        return icons.get(self.status, 'fa-circle')
    
    def get_status_color(self):
        """Return Bootstrap color class based on status"""
        colors = {
            'pending': 'warning',
            'reviewed': 'info',
            'shortlisted': 'primary',
            'interviewed': 'secondary',
            'offered': 'success',
            'hired': 'success',
            'rejected': 'danger',
            'withdrawn': 'dark text-white',
        }
        return colors.get(self.status, 'secondary')
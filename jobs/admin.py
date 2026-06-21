from django.contrib import admin
from .models import Job, JobCategory, JobApplication

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

from django.contrib import admin
from .models import Job, JobCategory, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'location', 'job_type', 'status', 'posted_by', 'posted_at')
    list_filter = ('status', 'job_type', 'experience_level', 'category', 'is_featured', 'is_remote')
    search_fields = ('title', 'company_name', 'location', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'posted_at'
    # Remove filter_horizontal if skills_required uses a through model
    # filter_horizontal = ('skills_required',)  # Comment this out
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'company_name', 'company_logo', 'company_website')
        }),
        ('Location & Type', {
            'fields': ('location', 'job_type', 'experience_level', 'is_remote')
        }),
        ('Salary', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'is_salary_negotiable')
        }),
        ('Details', {
            'fields': ('description', 'requirements', 'benefits')
        }),
        ('Skills', {
            'fields': ('skills_required',)
        }),
        ('Meta', {
            'fields': ('vacancies', 'application_deadline', 'status', 'is_featured', 'posted_by')
        }),
    )

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant__email', 'job__title')
    readonly_fields = ('applied_at',)
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('admin', 'Admin'),
    )
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='job_seeker')
    
    # Profile fields
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    portfolio_website = models.URLField(blank=True)
    
    # Resume
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # Skills
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    job_alerts = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_job_seeker(self):
        return self.user_type == 'job_seeker'
    
    def is_admin_user(self):
        return self.user_type == 'admin' or self.is_superuser
    
    def get_profile_completion(self):
        """Calculate profile completion percentage"""
        fields = [
            self.first_name,
            self.last_name,
            self.phone_number,
            self.bio,
            self.location,
            self.skills,
            self.resume,
            self.profile_picture,
            self.linkedin_profile or self.github_profile or self.portfolio_website,
        ]
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)
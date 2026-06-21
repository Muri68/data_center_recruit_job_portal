# Create your models here.
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # About section
    about_title = models.CharField(max_length=200)
    about_description = CKEditor5Field(config_name='extends', blank=True, null=True)
    mission = CKEditor5Field(config_name='extends', blank=True, null=True)
    vision = CKEditor5Field(config_name='extends', blank=True, null=True)

    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    google_map_embed = models.TextField(blank=True, help_text="Google Maps embed URL")
    
    # Social Media
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    
    # SEO
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Styling
    primary_color = models.CharField(max_length=7, default='#0d6efd')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    
    # Footer
    footer_text = models.TextField(blank=True)
    copyright_text = models.CharField(max_length=255, default='© 2024 Job Portal. All rights reserved.')
    
    # Advanced Settings
    custom_css = models.TextField(blank=True, help_text="Custom CSS code")
    custom_js = models.TextField(blank=True, help_text="Custom JavaScript code")
    google_analytics = models.CharField(max_length=50, blank=True, help_text="Google Analytics tracking ID")
    
    # Why Choose Us Section Headers
    why_choose_us_title = models.CharField(max_length=200, default="Why Choose Us")
    why_choose_us_subtitle = models.CharField(max_length=200, default="Why We Are the Right Choice")
    why_choose_us_description = models.TextField(blank=True, default="We connect employers and job seekers through a smart, efficient, and reliable hiring platform.")
    
    # FAQ Section Headers
    faq_title = models.CharField(max_length=200, default="Frequently Asked Questions")
    faq_subtitle = models.CharField(max_length=200, default="Find answers to common questions", blank=True)
    
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError('Only one Site Settings instance can exist')
        return super().save(*args, **kwargs)
    
    
    
class FAQ(models.Model):
    """Frequently Asked Questions model"""
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Order of appearance")
    is_active = models.BooleanField(default=True, help_text="Show/Hide this FAQ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.question[:80]
    
    
class WhyChooseUs(models.Model):
    """Why Choose Us features model"""
    icon = models.CharField(max_length=50, default="fas fa-star", help_text="Font Awesome icon class (e.g., fas fa-users)")
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Order of appearance")
    is_active = models.BooleanField(default=True, help_text="Show/Hide this feature")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Why Choose Us Feature'
        verbose_name_plural = 'Why Choose Us Features'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
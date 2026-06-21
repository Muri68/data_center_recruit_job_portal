from django.contrib import admin
from .models import SiteSettings, FAQ, WhyChooseUs

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('General', {
            'fields': ('site_name', 'tagline', 'logo', 'favicon')
        }),
        ('Branding', {
            'fields': ('primary_color', 'secondary_color')
        }),
        ('About Section', {
            'fields': ('about_title', 'about_description', 'mission', 'vision')
        }),
        ('Why Choose Us Section', {
            'fields': ('why_choose_us_title', 'why_choose_us_subtitle', 'why_choose_us_description')
        }),
        ('FAQ Section', {
            'fields': ('faq_title', 'faq_subtitle')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'google_map_embed')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'linkedin', 'instagram', 'youtube')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Footer', {
            'fields': ('footer_text', 'copyright_text')
        }),
        ('Advanced', {
            'fields': ('custom_css', 'custom_js', 'google_analytics'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.exists():
            return False
        return True


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active', 'created_at', 'updated_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')
    ordering = ('order', '-created_at')
    
    fieldsets = (
        (None, {
            'fields': ('question', 'answer')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(WhyChooseUs)
class WhyChooseUsAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active', 'created_at')
    list_editable = ('icon', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('order', '-created_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Icon', {
            'fields': ('icon',),
            'description': 'Enter Font Awesome icon class. Examples: fas fa-users, fas fa-rocket, fas fa-chart-line'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )
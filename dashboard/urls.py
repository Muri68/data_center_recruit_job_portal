from django.urls import path
from . import views
from . import admin_views

app_name = 'dashboard'

urlpatterns = [
    # Redirect
    path('', views.redirect_dashboard, name='redirect_dashboard'),
    
    # Job Seeker URLs
    path('seeker/', views.job_seeker_dashboard, name='job_seeker_dashboard'),
    path('applications/', views.my_applications, name='my_applications'),
    path('apply/<slug:job_slug>/', views.apply_job, name='apply_job'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Admin URLs
    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/applications/', admin_views.admin_applications, name='admin_applications'),
    path('admin/application/<int:application_id>/', admin_views.admin_application_detail, name='admin_application_detail'),
    path('admin/application/<int:application_id>/update-status/', admin_views.update_application_status, name='update_application_status'),
    path('admin/jobs/', admin_views.admin_jobs, name='admin_jobs'),
    path('admin/jobs/create/', admin_views.create_job, name='create_job'),
    path('admin/jobs/<int:job_id>/edit/', admin_views.edit_job, name='edit_job'),
    path('admin/jobs/<int:job_id>/delete/', admin_views.delete_job, name='delete_job'),
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('admin/settings/', admin_views.site_settings, name='site_settings'),
    path('admin/reports/', admin_views.admin_reports, name='admin_reports'),
    
    # Admin Profile URLs
    path('admin/profile/', admin_views.admin_profile, name='admin_profile'),
    path('admin/profile/update/', admin_views.admin_update_profile, name='admin_update_profile'),
    # Admin Change Password
    path('admin/change-password/', admin_views.admin_change_password, name='admin_change_password'),
    
    # FAQ Management
    path('admin/faqs/', admin_views.manage_faqs, name='admin_faqs'),
    path('admin/faqs/add/', admin_views.add_faq, name='admin_add_faq'),
    path('admin/faqs/<int:faq_id>/edit/', admin_views.edit_faq, name='admin_edit_faq'),
    path('admin/faqs/<int:faq_id>/delete/', admin_views.delete_faq, name='admin_delete_faq'),
    
    # Why Choose Us Management
    path('admin/why-choose-us/', admin_views.manage_why_choose_us, name='admin_why_choose_us'),
    path('admin/why-choose-us/add/', admin_views.add_why_choose_us, name='admin_add_why_choose_us'),
    path('admin/why-choose-us/<int:feature_id>/edit/', admin_views.edit_why_choose_us, name='admin_edit_why_choose_us'),
    path('admin/why-choose-us/<int:feature_id>/delete/', admin_views.delete_why_choose_us, name='admin_delete_why_choose_us'),
    
    
    # Blog Management
    path('admin/blog/', admin_views.admin_blog_posts, name='admin_blog_posts'),
    path('admin/blog/create/', admin_views.admin_create_blog_post, name='admin_create_blog_post'),
    path('admin/blog/<int:post_id>/edit/', admin_views.admin_edit_blog_post, name='admin_edit_blog_post'),
    path('admin/blog/<int:post_id>/delete/', admin_views.admin_delete_blog_post, name='admin_delete_blog_post'),
    
    # Blog Categories
    path('admin/blog/categories/', admin_views.admin_blog_categories, name='admin_blog_categories'),
    path('admin/blog/categories/<int:category_id>/edit/', admin_views.admin_edit_blog_category, name='admin_edit_blog_category'),
    path('admin/blog/categories/<int:category_id>/delete/', admin_views.admin_delete_blog_category, name='admin_delete_blog_category'),
    
    # Blog Comments
    path('admin/blog/comments/', admin_views.admin_blog_comments, name='admin_blog_comments'),
    path('admin/blog/comments/<int:comment_id>/toggle/', admin_views.admin_toggle_comment, name='admin_toggle_comment'),
    path('admin/blog/comments/<int:comment_id>/delete/', admin_views.admin_delete_blog_comment, name='admin_delete_blog_comment'),
]
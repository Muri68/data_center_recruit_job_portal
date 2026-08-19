from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory, BlogComment

# views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count, Q
from taggit.models import Tag
from .models import BlogPost, BlogCategory

def post_list(request):
    # Base queryset
    posts = BlogPost.objects.filter(status='published').select_related('category', 'author')
    
    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Tag filter
    tag_slug = request.GET.get('tag', '')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Search filter
    query = request.GET.get('q', '')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query)
        )
    
    # Get total posts count before pagination
    total_posts_count = BlogPost.objects.filter(status='published').count()
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get categories with post counts
    categories = BlogCategory.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)
    
    # Get recent posts for sidebar (always show latest 5 published posts)
    recent_posts = BlogPost.objects.filter(
        status='published'
    ).select_related('category', 'author').order_by('-published_at')[:5]
    
    # Get popular tags with usage counts
    popular_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]
    
    context = {
        'posts': posts,
        'categories': categories,
        'category_slug': category_slug,
        'tag_slug': tag_slug,
        'popular_tags': popular_tags,
        'recent_posts': recent_posts,
        'total_posts_count': total_posts_count,
        'query': query,
        'page_title': 'Blog',
    }
    return render(request, 'blog/post_list.html', context)


# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from taggit.models import Tag
from .models import BlogPost, BlogCategory, BlogComment

def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    post.views_count += 1
    post.save()
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id).select_related('category', 'author')[:3]
    
    # Get recent posts for sidebar
    recent_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(id=post.id).select_related('category', 'author').order_by('-published_at')[:5]
    
    # Get categories with post counts
    categories = BlogCategory.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        num_times=Count('taggit_taggeditem_items')
    ).order_by('-num_times')[:10]
    
    # Get total posts count
    total_posts_count = BlogPost.objects.filter(status='published').count()
    
    # Handle comments
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            BlogComment.objects.create(
                post=post,
                user=request.user,
                content=content
            )
            return redirect('blog:post_detail', slug=slug)
    
    comments = post.comments.filter(is_approved=True)
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
        'recent_posts': recent_posts,
        'categories': categories,
        'popular_tags': popular_tags,
        'total_posts_count': total_posts_count,
        'page_title': post.title,
    }
    return render(request, 'blog/post_detail.html', context)
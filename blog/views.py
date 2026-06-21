from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory, BlogComment

def post_list(request):
    posts = BlogPost.objects.filter(status='published')
    
    category_slug = request.GET.get('category', '')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    categories = BlogCategory.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'category_slug': category_slug,
        'page_title': 'Blog',
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    post.views_count += 1
    post.save()
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:3]
    
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
        'page_title': post.title,
    }
    return render(request, 'blog/post_detail.html', context)
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden 
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
from .models import TravelPost, Comment
from .forms import PostForm, CommentForm
from .models import ContactMessage
from .models import Message

# Home View
def home(request):
    query = request.GET.get('q')
    if query:
        posts_list = TravelPost.objects.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        ).distinct().order_by('-created_at')
    else:
        posts_list = TravelPost.objects.all().order_by('-created_at')

    paginator = Paginator(posts_list, 6) 
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'blog/home.html', {'posts': posts})

# Create Post
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Your adventure has been shared!")
            return redirect('blog-home') 
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

# Post Detail & Comment Logic
def post_detail(request, pk):
    post = get_object_or_404(TravelPost, pk=pk)
    comments = post.comments.filter(parent=None).order_by('-created_at')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                comment.parent = parent_obj
            
            comment.save()
            messages.success(request, "Comment added!")
            return redirect(reverse('post-detail', kwargs={'pk': post.pk}) + '#comment-section')
    else:
        form = CommentForm()
        
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': form
    })

# Update Post
@login_required
def post_update(request, pk):
    post = get_object_or_404(TravelPost, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")
        
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Your post has been updated!")
            return redirect('post-detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Update Post'})

# Delete Post
@login_required
def post_delete(request, pk):
    post = get_object_or_404(TravelPost, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden()
        
    if request.method == 'POST':
        post.delete()
        messages.warning(request, "Post deleted successfully.")
        return redirect('blog-home')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

# Edit Comment
@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return HttpResponseForbidden("You cannot edit this comment.")
        
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated!")
            return redirect(reverse('post-detail', kwargs={'pk': comment.post.pk}) + '#comment-section')
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment_edit.html', {'form': form, 'comment': comment})

# Delete Comment
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author == request.user:
        post_id = comment.post.pk
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect(reverse('post-detail', kwargs={'pk': post_id}) + '#comment-section')
    return HttpResponseForbidden()

@login_required
def post_like(request, pk):
    post = get_object_or_404(TravelPost, id=pk)
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'total_likes': post.total_likes()
    })

def about(request):
    return render(request, 'blog/about.html', {'title': 'About Us'})

def contact(request):
    return render(request, 'blog/contact.html', {'title': 'Contact Us'})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_content = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_content
        )
        
        messages.success(request, 'သင့် Message ပို့ပြီးပါပြီ။ မကြာမီ ပြန်လည်ဆက်သွယ်ပေးပါမည်။')
        return redirect('blog-contact')

    return render(request, 'blog/contact.html')

def privacy_policy(request):
    return render(request, 'blog/privacy.html', {'title': 'Privacy Policy'})

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'blog/inbox.html', {'messages': messages})


@login_required
def chat_room(request, username):
    recipient = get_object_or_404(User, username=username)
    
    if recipient == request.user:
        messages.warning(request, "ကိုယ့်ဘာသာကိုယ် စာပို့၍မရပါ။")
        return redirect('blog-home')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=recipient,
                content=content
            )
            return redirect('chat-room', username=username)

    chat_messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=recipient)) |
        (Q(sender=recipient) & Q(receiver=request.user))
    ).order_by('timestamp')

    return render(request, 'blog/chat_room.html', {
        'recipient': recipient,
        'chat_messages': chat_messages
    })

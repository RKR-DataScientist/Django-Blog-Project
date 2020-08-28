from django.shortcuts import render
from django.http import Http404
from .models import Post, Author, subscribe, Contact, Comment, SubComment
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

# Create your views here.
def home(request):

    # For email subsriber
    if request.method == "GET":
        email = request.GET.get('email')
        if email:
            subscribe(email = email).save()
    
    # For Trending Code
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    trends = Post.objects.filter(time_upload__gte = week_ago).order_by('-read')

    # Filter the top 5 author and thier first post
    TopAuthor = Author.objects.order_by('-rate')[:4]
    AuthorPost = [Post.objects.filter(auther = author).first() for author in TopAuthor]
    all_post = Paginator(Post.objects.filter(publish=True),3)
    page = request.GET.get('page')
    try:
        posts = all_post.page(page)
    except PageNotAnInteger:
        posts = all_post.page(1)
    except EmptyPage:
        posts = all_post.page(all_post.num_pages)
    parms = {
        #'posts': Post.objects.all(), --- It will fetch all the post, but we want only published post
        #'posts' : Post.objects.filter(publish=True),--- We have created paginator and passed all post through that
        'posts' : posts,
        'trending_post' : trends[:5],
        'author_post' : AuthorPost,
        'pop_post' : Post.objects.order_by('-read')[:9],
    }    
    return render(request, 'index.html', parms)


def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':

        name = f"{request.POST.get('fname')} {request.POST.get('lname')}"
        email = request.POST.get('email')
        mobile = request.POST.get('mob')
        mess = request.POST.get('mess', 'default')

        Contact(name=name, email=email, mobile=mobile, mess=mess).save()
    
    return render(request, 'contact.html')

def post(request, id, slug):
    try:
        post = Post.objects.get(pk = id, slug = slug)
    except :
        raise Http404(" Post doesn't exist ")

    post.read+=1
    post.save()
    if request.method == 'POST':
        comm = request.POSt.get('comm')
        comm_id = request.POST.get('comm_id')

        if comm_id:
            SubComment(post = post,
            user = request.user,
            comm = comm,
            comment = Comment.objects.get(id=int(comm_id))
            ).save()
        else:
            Comment(post = post, user = request.user,comm = comm).save()
    comments = []
    for c in Comment.objects.filter(post=post):
        comments.append([c, Comment.objects.filter(comment=c)])

    parms={
        'post':post,
        'comments' : comments,
        'pop_post': Post.objects.order_by('-read')[:9],
    }
    return render(request, 'blog.html', parms)

def search(request):
    q = request.GET.get('q')
    posts = Post.objects.filter(
        Q(title__icontains = q) |
        Q(overview__icontains = q)
    ).distinct()

    parms = {
        'posts' : posts,
        'title' : f'Result for :- {q}',
        'pop_post' : Post.objects.order_by('-read')[:9],
    }
    return render(request, 'search.html', parms)
    
def view_all(request, query):
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    acpt = ['trending', 'popular']
    q = query.lower()
    if q in acpt:
        if q == 'trending':
            parms = {
                'posts' : Post.objects.filter(time_upload__gte = week_ago).order_by('-read'),
                'title' : 'Trending Post',
                'pop_post' : Post.objects.order_by('-read')[:9],
            }
        elif q == 'popular':
            parms = {
                'posts': Post.objects.order_by('-read'),
                'title' : 'Popular Post',
                'pop_post' : Post.objects.order_by('-read')[:9],
            }
    else:
        pass
    return render(request, 'view_all.html', parms)
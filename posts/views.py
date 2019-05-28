from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.db.models import Count, Q

from django.views.generic.edit import FormView


from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.views.generic.base import View


from .models import Post, Author, PostView
from .forms import CommentForm, PostForm




class RegisterFormView(FormView):
	form_class = UserCreationForm
	success_url = "/login"
	template_name = "account/signup.html"


	def form_valid(self, form):
		form.save()
		return super(RegisterFormView, self).form_valid(form)




class LoginFormView(FormView):
	form_class = AuthenticationForm
	template_name = "account/login.html"
	success_url = "/"


	def form_valid(self, form):
		self.user = form.get_user()
		login(self.request, self.user)
		return super(LoginFormView, self).form_valid(form)



class LogoutView(View):
	

	def get(self, request):
		logout(request)
		return HttpResponseRedirect("/")



def get_author(user):
	queryset = Author.objects.filter(user=user)
	if queryset.exists():
		return queryset[0]
	return None


def search(request):
	queryset = Post.objects.all()
	query = request.GET.get('q')
	if query:
		queryset = queryset.filter(
			Q(title__icontains=query) | Q(body__icontains=query)
		).distinct()
	context = {
		'query': queryset
	}
	return render(request, 'search_results.html', context)




def get_category_count():
	categories = Post.objects.values('category__title').annotate(Count('category__title'))
	return categories



def index(request):
	featured_posts = Post.objects.filter(featured=True)[0:3]
	latest_posts = Post.objects.order_by('-pub_time')[0:3]
	context = {
		'featured_posts' : featured_posts,
		'latest_posts' : latest_posts
	}
	return render(request, 'index.html', context)


def blog(request):
	category_count = get_category_count()
	most_recent = Post.objects.order_by('-pub_time')[:3]
	posts = Post.objects.all()
	paginator = Paginator(posts, 4)
	page_request_var = 'page'
	page = request.GET.get(page_request_var)

	try:
		paginated_queryset = paginator.page(page)
	except PageNotAnInteger:
		paginated_queryset = paginator.page(1)
	except EmptyPage:
		paginated_queryset = paginator.page(paginator.num_pages)

	context = {
		'posts': paginated_queryset,
		'most_recent': most_recent,
		'page_request_var': page_request_var,
		'category_count': category_count
	}
	return render(request, 'blog.html', context)


def post(request, id):
	category_count = get_category_count()
	most_recent = Post.objects.order_by('-pub_time')[:3]
	post = get_object_or_404(Post, id=id)

	if request.user.is_authenticated:
		PostView.objects.get_or_create(user=request.user, post=post)

	form = CommentForm(request.POST or None)
	if request.method == "POST":
		if form.is_valid():
			form.instance.user = request.user
			form.instance.post = post
			form.save()
			return redirect(reverse("post-detail", kwargs={
				'id': post.id
			}))
	context = {
		'form': form,
		'post': post,
		'most_recent': most_recent,
		'category_count': category_count
	}
	return render(request, 'post.html', context)


def post_create(request):
	title = 'Cоздание'
	form = PostForm(request.POST or None, request.FILES or None)
	author = get_author(request.user)
	if request.method == "POST":
		if form.is_valid():
			form.instance.author = author
			form.save()
			return redirect(reverse("post-detail", kwargs={
				'id': form.instance.id
			}))
	context = {
		'title': title,
		'form': form
	}
	return render(request, "post_create.html", context)


def post_update(request,id):
	title = 'Изменение'
	post = get_object_or_404(Post, id=id)
	form = PostForm(
		request.POST or None,
		request.FILES or None,
		instance=post)
	author = get_author(request.user)
	if request.method == "POST":
		if form.is_valid():
			form.instance.author = author
			form.save()
			return redirect(reverse("post-detail", kwargs={
				'id': form.instance.id
			}))
	context = {
		'title': title,
		'form': form
	}
	return render(request, "post_create.html", context)

def post_delete(request,id):
	post = get_object_or_404(Post, id=id)
	post.delete()
	return redirect(reverse("post-list"))
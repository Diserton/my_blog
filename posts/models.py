from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()



class Author(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	profile_img = models.ImageField()


	def __str__(self):
		return self.user.username



class Category(models.Model):
	title = models.CharField(max_length=50)


	def __str__(self):
		return self.title



class Post(models.Model):
	title = models.CharField(max_length=150)
	body = models.TextField()
	pub_time = models.DateTimeField(auto_now_add=True)
	comment_count = models.IntegerField(default=0)
	author = models.ForeignKey(Author, on_delete=models.CASCADE)
	img = models.ImageField()
	category = models.ManyToManyField(Category)
	featured = models.BooleanField()


	def __str__(self):
		return self.title

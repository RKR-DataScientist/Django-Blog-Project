from django.contrib import admin
from .models import Post, Author, Category, subscribe, Contact
# Register your models here.

admin.site.register(Post)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(subscribe)
admin.site.register(Contact)

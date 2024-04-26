from django.contrib import admin
from .models import User, GameResult, Photo
# Register your models here.
admin.site.register(User)
admin.site.register(GameResult)
admin.site.register(Photo)
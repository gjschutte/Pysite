from django.contrib import admin

from .models import Province, Route, RouteComment, RoutePhoto, Type

# Register your models here.

admin.site.register(Route)
admin.site.register(RouteComment)
admin.site.register(RoutePhoto)
admin.site.register(Province)
admin.site.register(Type)

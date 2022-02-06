from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('routes/', views.RouteListView.as_view(), name='routes'),
    path('route/<int:pk>', views.RouteDetailView.as_view(), name='route-detail'),
    path('route/create/', views.CreateRoute, name='route-create'),
    path('route/<int:pk>/createcomment', views.CreateRouteComment, name='create-route-comment'),
    path('route/<int:pk>/createphoto', views.AddImage, name='add-image'),
    path('routes/map/', views.RouteMapAll, name='route-map'),
]

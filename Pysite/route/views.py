from django.shortcuts import render
from django.views import generic
import folium
from folium import IFrame
import gpxpy
import gpxpy.gpx
import os
from django.conf import settings
from django.contrib.auth import get_user
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .models import Route, Type, Province, RouteComment, RoutePhoto
from route.forms import CreateRouteForm, AddImageForm, CreateRouteCommentForm

# Create your views here.

def get_route_info(routeset):
    # Generic function to retrieve some data about a set of routes
    route_info = []
    for route in routeset:

        route = get_object_or_404(Route, pk=route.id)

        # Select 1 picture per route
        pics = RoutePhoto.objects.filter(route=route.id)[:1]    
        if len(pics) != 0:
            for pic in pics:
                route.photo = pic.image
        else:
            route.photo = "No pic"            
        route_info.append(route)
    return route_info

def index(request):
    """View function for home page of the site"""

    # Generate count of some of the main objects
    num_route = Route.objects.all().count()
    # Select the total distance walked
    tot_distance = Route.objects.aggregate(Sum('length'))

    # Select latest 3 routes
    latest = RouteComment.objects.all().order_by('-date')[:3]
    latest_routes = get_route_info(latest)

    # Select 3 routes with the highest score
    highest = RouteComment.objects.annotate().order_by('-score')[:3]
    highest_routes = get_route_info(highest)

    context = {
        'num_route': num_route,
        'tot_distance': tot_distance["length__sum"],
        'latest_routes': latest_routes,
        'highest_routes': highest_routes,
    }

    # Render the HTML template index.html with the data from context
    return render(request, 'index.html', context=context)

def RouteListByTypeView (request, sel, pk):
    """ View function to list the routes by type """
    context = {}
    # Select the routes
    print(sel)
    if sel == 1:
        route_text = 'All available routes'
        route_list = Route.objects.all()
    if sel == 2:
        route_list = Route.objects.filter(type = pk)
        type_name = Type.objects.get(pk=pk)
        route_text = 'Routes by type: {}'.format(type_name)
    if sel == 3:
        route_list = Route.objects.filter(province=pk)
        province_name = Province.objects.get(pk=pk)
        route_text = 'Routes by province: {}'.format(province_name)

    route_set = get_route_info(route_list)

    # Select the route types
    types = Type.objects.all()

    # Select the provinces
    provinces = Province.objects.all()
    
    context = {
        'route_list': route_set,
        'route_text': route_text,
        'types': types,
        'provinces': provinces,
    }

    return render(request, 'route_list.html', context= context)


class RouteDetailView(generic.DetailView):
    model = Route

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(RouteDetailView, self).get_context_data(**kwargs)

        gpxfile = self.object.gpx

        filename = os.path.join(settings.MEDIA_ROOT, gpxfile.name)
        f = open(filename, 'r')
        gpx = gpxpy.parse(f)
        f.close()

        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(tuple([point.latitude, point.longitude]))

        ave_lat = sum(p[0] for p in points)/len(points)
        ave_lon = sum(p[1] for p in points)/len(points)

        figure = folium.Figure()
        # Load map centered on average coordinates
        my_map = folium.Map(
            location = [ave_lat, ave_lon], 
            zoom_start=13,
            width=800,
            height=500
        )
        my_map.add_to(figure)

        # Add route to map
        folium.PolyLine(points, color = "red", weight=2.5, opacity=1).add_to(my_map)

        # Add starting point to map
        folium.Marker(
            location = points[0],
            popup = self.object.name,
            icon = folium.Icon(color="blue", icon="info-sign"),
        ).add_to(my_map)

        figure.render()

        context['map'] = figure

        return context

def CreateRoute(request):
    new_route = None

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding)
        form = CreateRouteForm(request.POST, request.FILES)

        if form.is_valid():
            # Create RouteBeschrijving object but don't save to database yet
            new_route = form.save(commit=False)
            # Assign the current User to the Route
            user = get_user(request)
            new_route.author = user
            new_route.save()

            # Redirect to a new URL
            return HttpResponseRedirect(reverse('routes') )

    # If this is a get (or any other method) create the default form.
    else:
        form = CreateRouteForm()
    
    context = {
        'form': form,    
    }

    return render(request, 'route/route_form.html', context)

@login_required
def CreateRouteComment(request, pk):
    route = get_object_or_404(Route, pk=pk)
    new_routecomment = None

    # If this is a POST request then process the form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding)
        form = CreateRouteCommentForm(request.POST)

        # Check if the form is valid
        if form.is_valid():
            # Create RouteComment object but don't save to database yet
            new_routecomment = form.save(commit=False)
            # Assign the current Route to the RouteComment
            new_routecomment.route = route
            # Assign the current User to the RouteComment
            user = get_user(request)
            new_routecomment.author = user

            new_routecomment.save()

            # Redirect to a new URL
            url = reverse('route-detail', kwargs={'pk': route.id})
            return HttpResponseRedirect(url)

    else:
        form = CreateRouteCommentForm()

    context = {
        'form': form,
        'route': route,
    }

    return render(request, 'route/routecomment_form.html', context)


def AddImage(request, pk):
    route = get_object_or_404(Route, pk=pk)
    new_routephoto = None

    # If this is a POST request then process the form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding)
        form = AddImageForm(request.POST, request.FILES)
        print (form)

        # Check if the form is valid
        if form.is_valid():
            # Create RoutePhoto object but don't save to database yet
            new_routephoto = form.save(commit=False)
            # Assign the current Route to the Routephoto
            new_routephoto.route = route
            # Assign the current User to the Routephoto
            user = get_user(request)
            new_routephoto.author = user
            new_routephoto.save()

            # Redirect to a new URL
            url = reverse('route-detail', kwargs={'pk': route.id})
            return HttpResponseRedirect(url)

    else:
        form = AddImageForm()

    context = {
        'form': form,
        'route': route,
    }

    return render(request, 'route/add_image_form.html', context)

def RouteMapAll(request):
    """View function for all the routes in 1 map"""

    # Select all the routes with a gpx-file
    all_routes = Route.objects.exclude(gpx__isnull=True).exclude(gpx__exact='').count()

    routes = Route.objects.exclude(gpx__isnull=True).exclude(gpx__exact='')

    # Average longitude and latitude, to center the map
    # For now, it's Apeldoorn.
    ave_lat = 52.211157
    ave_lon = 5.9699231

    figure = folium.Figure()
    # Load map centered on average coordinates
    my_map = folium.Map(
        location = [ave_lat, ave_lon], 
        zoom_start=11,
        width=900,
        height=700
    )
    my_map.add_to(figure)

    for hike in routes:

        print (hike.type)
        if hike.type.name == "Trage Tocht":
            color = "blue"
        else:
            if hike.type.name == "Klompenpad":
                color = "red"
            else:
                color = "green"

        gpxfile = hike.gpx

        filename = os.path.join(settings.MEDIA_ROOT, gpxfile.name)
        f = open(filename, 'r')
        gpx = gpxpy.parse(f)
        f.close()

        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(tuple([point.latitude, point.longitude]))

        # Add route to map
        folium.PolyLine(points, color = color, popup = hike.name, weight=2.5, opacity=1).add_to(my_map)

    figure.render()

    context = {
        'all_routes': all_routes,
        'map': figure,
    }

    # Render the HTML template index.html with the data from context
    return render(request, 'routemap.html', context=context)

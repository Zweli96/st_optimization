from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Facility, District, Health_Worker, Courier, Route
from .forms import DistrictForm, FacilityForm, Health_WorkerForm, CreateUserForm, CourierForm
from datetime import date, datetime, timedelta
from django.utils.timezone import localtime
from .commcare_submsission_api.submit_data import main
from django.forms.models import model_to_dict
from django.core import serializers
import json


# Create your views here.


def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Wrong username or password')
    context = {}
    return render(request, 'sample_volumes/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def registerUser(request):
    form = CreateUserForm

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('/volumes')
    context = {'form': form}
    return render(request, 'sample_volumes/register_user.html', context)


def dashboard(request, pk=''):

    context = {}
    districts = District.objects.order_by('name')

    selected_district = ""

    if request.method == 'POST':
        selected_district = request.POST['district']

    if selected_district:
        context.update({'selected_district': selected_district})
        facilities = Facility.objects.filter(district=selected_district)
        facility_count = facilities.count()
    else:
        print('no selected_district')
        facilities = Facility.objects.all()
        facility_count = facilities.count()

    context.update({'facilities': facilities,
                   'facility_count': facility_count, 'districts': districts})

    return render(request, 'sample_volumes/dashboard.html', context)


def sample_volumes(request):
    return render(request, 'sample_volumes/sample_volumes.html')


def facilities(request):
    facilities = Facility.objects.all()
    context = {'facilities': facilities}
    return render(request, 'sample_volumes/facilities.html', context)


def health_workers(request):
    health_workers = Health_Worker.objects.all()
    context = {'health_workers': health_workers}
    return render(request, 'sample_volumes/health_workers.html', context)


def couriers(request):
    couriers = Courier.objects.all()
    context = {'couriers': couriers}
    return render(request, 'sample_volumes/couriers.html', context)


def districts(request):
    districts = District.objects.all()
    context = {'districts': districts}
    return render(request, 'sample_volumes/districts.html', context)


def createDistrict(request):
    form = DistrictForm
    context = {'form': form}

    if request.method == 'POST':
        # print('Printing POST: ', request.POST)
        form = DistrictForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'sample_volumes/district_form.html', context)


def updateDistrict(request, pk):
    district = District.objects.get(id=pk)
    form = DistrictForm(instance=district)

    if request.method == 'POST':
        # print('Printing POST: ', request.POST)
        form = DistrictForm(request.POST, instance=district)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'sample_volumes/district_form.html', context)


def deleteDistrict(request, pk):
    district = District.objects.get(id=pk)
    if request.method == "POST":
        district.delete()
        return redirect('home')
    context = {'item': district}
    return render(request, 'sample_volumes/delete.html', context)


def createFacility(request):
    form = FacilityForm
    context = {'form': form}

    if request.method == 'POST':
        # print('Printing POST: ', request.POST)
        form = FacilityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'sample_volumes/facility_form.html', context)


def updateFacility(request, pk):
    facility = Facility.objects.get(id=pk)
    form = FacilityForm(instance=facility)

    if request.method == 'POST':
        # print('Printing POST: ', request.POST)
        form = FacilityForm(request.POST, instance=facility)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'sample_volumes/facility_form.html', context)


def deleteFacility(request, pk):
    facility = Facility.objects.get(id=pk)
    if request.method == "POST":
        facility.delete()
        return redirect('home')
    context = {'item': facility}
    return render(request, 'sample_volumes/delete.html', context)


def createHealth_Worker(request):
    form = Health_WorkerForm
    context = {'form': form}

    if request.method == 'POST':
        # print('Printing POST: ', request.POST)
        form = Health_WorkerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'sample_volumes/health_worker_form.html', context)


def createCourier(request):
    form = CourierForm()
    context = {'form': form}

    if request.method == 'POST':
        # print('Printing POST: ', request.POST)
        form = CourierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    return render(request, 'sample_volumes/courier_form.html', context)


def updateHealth_Worker(request, pk):
    health_worker = Health_Worker.objects.get(id=pk)
    form = Health_WorkerForm(instance=health_worker)

    if request.method == 'POST':
        # print('Printing POST: ', request.POST)
        form = Health_WorkerForm(request.POST, instance=health_worker)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'sample_volumes/health_worker_form.html', context)


def deleteHealth_Worker(request, pk):
    health_worker = Health_Worker.objects.get(id=pk)
    if request.method == "POST":
        health_worker.delete()
        return redirect('home')
    context = {'item': health_worker}
    return render(request, 'sample_volumes/delete.html', context)


def makeRoutes(request, pk=""):
    context = {}
    districts = District.objects.order_by('name')
    date_list = []

    route_status = {"status": "not_published",
                    "badge_color": "danger",
                    "display_text": "Not Saved",
                    "button_text": "Save Routes"}

    for i in range(0, 7):
        date_list.append({
            "index": i,
            "date": (datetime.now() - timedelta(days=i)),
            "date_string": (datetime.now() - timedelta(days=i)).strftime("%a-%d-%b")
        })

    date_list.reverse()

    facilities = ""

    selected_district = ""
    courier_count = 0

    if request.method == 'POST':
        route_date = date.today() + timedelta(days=1)
        if 'district' in request.POST:
            # if you have selected a district show information on when route was saved
            selected_district = districts.get(id=request.POST['district'])
            tomorrows_routes = Route.objects.filter(
                district=selected_district.id, route_date=route_date).order_by('-created_at')
            # if the route has been created
            if tomorrows_routes.count() > 0:
                tr = tomorrows_routes.first()
                route_created_by = tr.created_by
                route_created_at = localtime(tr.created_at)
                route_created_at = route_created_at.strftime(
                    "%a, %d %b %I:%M %p")
                route_status['status'] = 'published'
                route_status['badge_color'] = 'success'
                route_status['display_text'] = f'Saved on {route_created_at} by {route_created_by}'
                route_status['button_text'] = 'Update Routes'

        # When you click save or update routes check if all
        if all(params in request.POST for params in ('routes', 'selected_district', 'courier_count')):
            routes = json.loads(request.POST['routes'])
            selected_district = json.loads(request.POST['selected_district'])
            courier_count = json.loads(request.POST['courier_count'])
            user_id = json.loads(request.POST['user_id'])
            route_date = date.today() + timedelta(days=1)
            created_routes = []
            updated = True

            selected_district = District.objects.get(id=selected_district)
            route_number = 1
            for route in routes:
                # Check if route exists or a new one is being created.
                created_route = Route.objects.filter(
                    district=selected_district, route_date=route_date, route_number=route_number).first()
                if created_route is None:
                    created_route = Route(route_number=route_number,
                                          route_date=route_date, district=selected_district, created_by=User.objects.get(id=user_id))
                    created_route.save()
                    updated = False

                created_route.facilities.set(Facility.objects.filter(
                    id__in=route['facilities']), through_defaults={'created': datetime.now()})
                created_route.save()

                created_routes.append(model_to_dict(created_route))
                route_number += 1
            success, message = main(created_routes, updated)

            if request.is_ajax():
                return JsonResponse({'created_routes': 'created successfully'}, status=200)

            print('Hello')

    if selected_district:
        context.update({'selected_district': selected_district})
        facilities = Facility.objects.filter(district=selected_district.id)
        courier_count = Courier.objects.filter(
            district=selected_district.id).count()

    context.update({'districts': districts,
                   'route_status': route_status, 'facilities': facilities,
                    'date_list': date_list, 'courier_count': range(courier_count)})

    return render(request, 'sample_volumes/make_routes.html', context)


def viewRoutes(request):
    routes = []
    districts = District.objects.order_by('name')
    route_date = date.today() + timedelta(days=1)

    if request.method == 'POST':
        if 'date' in request.POST:
            route_date = request.POST['date']

    for district in districts:
        num_of_couriers = District.objects.get(
            id=district.id).courier_set.count()
        district_routes = Route.objects.filter(district=district.id, route_date=route_date).order_by(
            '-created_at')[:num_of_couriers]
        routes += district_routes

    context = {'routes': routes}
    return render(request, 'sample_volumes/routes.html', context)

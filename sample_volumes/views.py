from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Facility, District, Health_Worker, Courier
from .forms import DistrictForm, FacilityForm, Health_WorkerForm, CreateUserForm
from datetime import datetime, timedelta


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

    for i in range(0, 7):
        date_list.append({
            "index": i,
            "date": (datetime.now() - timedelta(days=i)),
            "date_string": (datetime.now() - timedelta(days=i)).strftime("%a-%d-%b")
        })

    date_list.reverse()

    facilities = ""

    selected_district = ""

    if request.method == 'POST':
        selected_district = districts.get(id=request.POST['district'])

    if selected_district:
        context.update({'selected_district': selected_district})
        facilities = Facility.objects.filter(district=selected_district.id)

    route_status = {"status": "not_published",
                    "badge_color": "danger",
                    "display_text": "Not Published", }

    context.update({'districts': districts,
                   'route_status': route_status, 'facilities': facilities, 'date_list': date_list})
    return render(request, 'sample_volumes/make_routes.html', context)

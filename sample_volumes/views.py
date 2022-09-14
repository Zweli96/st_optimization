from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile


from .models import (
    Sample_Volumes,
    Facility,
    District,
    Health_Worker,
    Courier,
    Route,
    FacilityGroup,
    SAMPLE_TYPE,
    DataUpdate
)
from .forms import (
    DistrictForm,
    FacilityForm,
    Health_WorkerForm,
    CreateUserForm,
    CourierForm,
    FacilityGroupForm,
    PasswordResetCustomForm
)
from datetime import date, datetime, timedelta
from django.utils.timezone import localtime
from .commcare_submsission_api.submit_data import main
from django.forms.models import model_to_dict
from django.core import serializers
from django.db.models import Q

from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

import os
import json


# Create your views here.
ACTIONS = (
    ("CREATE", "Create"),
    ("UPDATE", "Update"),
    ("DELETE", "Delete"),
    ("RESET PASSWORD", "Reset Password"),
)


def loginPage(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.info(request, "Wrong username or password")
    context = {}
    return render(request, "sample_volumes/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


def registerUser(request):
    form = CreateUserForm

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")
            messages.success(request, "Account was created for " + user)
            return redirect("/volumes")
    context = {"form": form}
    return render(request, "sample_volumes/register_user.html", context)


def dashboard(request, pk=""):

    context = {}
    districts = District.objects.order_by("name")
    selected_date = datetime.today()

    selected_district = ""

    last_update = DataUpdate.objects.filter(
        completed=True).order_by('-created_at').first()
    current_update = DataUpdate.objects.filter(completed=False)

    last_update_time = last_update.created_at
    currently_updating = False
    if current_update:
        currently_updating = True

    if request.method == "POST":
        selected_district = request.POST["district"]
        if request.POST["date"]:
            selected_date = datetime.strptime(request.POST["date"], "%Y-%m-%d")
            context.update({"selected_date": selected_date})
            #context.update({"selected_date": request.POST["date"]})

    if selected_district:
        context.update({"selected_district": selected_district})
        facilities = Facility.objects.filter(district=selected_district)
        facility_count = facilities.count()
        reported_facilities_count = len(Sample_Volumes.objects.filter(facility__district=selected_district,
                                                                      reported_date__year=selected_date.year, reported_date__month=selected_date.month, reported_date__day=selected_date.day).values_list('facility', flat=True).distinct())
        non_reporting_count = facility_count - reported_facilities_count
        reporting_percentage = int(
            reported_facilities_count/facility_count * 100.0)
    else:
        facilities = Facility.objects.all()
        facility_count = facilities.count()
        reported_facilities_count = len(Sample_Volumes.objects.filter(
            reported_date__year=selected_date.year, reported_date__month=selected_date.month, reported_date__day=selected_date.day).values_list('facility', flat=True).distinct())
        non_reporting_count = facility_count - reported_facilities_count
        reporting_percentage = int(
            reported_facilities_count/facility_count * 100.0)

    context.update(
        {
            "facilities": facilities,
            "facility_count": facility_count,
            "districts": districts,
            "selected_district": selected_district,
            "selected_date": selected_date,
            "reported_facilities_count": reported_facilities_count,
            "non_reporting_count": non_reporting_count,
            "reporting_percentage": reporting_percentage,
            "last_update_time": last_update_time,
            "currently_updating": currently_updating

        }
    )

    return render(request, "sample_volumes/dashboard.html", context)


def sample_volumes(request):
    return render(request, "sample_volumes/sample_volumes.html")


def facilities(request):
    facilities = Facility.objects.all()
    context = {"facilities": facilities}
    return render(request, "sample_volumes/facilities.html", context)


def health_workers(request):
    health_workers = Health_Worker.objects.all()
    context = {"health_workers": health_workers}
    return render(request, "sample_volumes/health_workers.html", context)


def couriers(request):
    couriers = Courier.objects.all()
    context = {"couriers": couriers}
    return render(request, "sample_volumes/couriers.html", context)


def districts(request):
    districts = District.objects.all()
    context = {"districts": districts}
    return render(request, "sample_volumes/districts.html", context)


def createDistrict(request):
    form = DistrictForm
    action = ACTIONS[0][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = DistrictForm(request.POST)
        if form.is_valid():
            form.save()
            district = form.cleaned_data.get("name")
            messages.success(request, f"District {district} was created")
            return redirect("districts")

    return render(request, "sample_volumes/district_form.html", context)


def updateDistrict(request, pk):

    district = District.objects.get(id=pk)
    form = DistrictForm(instance=district)
    action = ACTIONS[1][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = DistrictForm(request.POST, instance=district)
        if form.is_valid():
            form.save()
            messages.success(request, f"District {district.name} was updated")
            return redirect("districts")

    return render(request, "sample_volumes/district_form.html", context)


def deleteDistrict(request, pk):
    district = District.objects.get(id=pk)
    if request.method == "POST":
        messages.success(request, f"District {district.name} was deleted")
        district.delete()
        return redirect("districts")
    context = {"item": district}
    return render(request, "sample_volumes/delete.html", context)


def createFacility(request):
    form = FacilityForm
    action = ACTIONS[0][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = FacilityForm(request.POST)
        if form.is_valid():
            form.save()
            facility = form.cleaned_data.get("name")
            messages.success(request, f"Facility {facility} was created")
            return redirect("facilities")

    return render(request, "sample_volumes/facility_form.html", context)


def updateFacility(request, pk):
    facility = Facility.objects.get(id=pk)
    form = FacilityForm(instance=facility)
    action = ACTIONS[1][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = FacilityForm(request.POST, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, f"Facility {facility.name} was updated")
            return redirect("facilities")

    return render(request, "sample_volumes/facility_form.html", context)


def deleteFacility(request, pk):
    facility = Facility.objects.get(id=pk)
    if request.method == "POST":
        messages.success(request, f"Facility {facility.name} was deleted")
        facility.delete()
        return redirect("facilities")
    context = {"item": facility}
    return render(request, "sample_volumes/delete.html", context)


def createHealth_Worker(request):
    form = Health_WorkerForm
    action = ACTIONS[0][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = Health_WorkerForm(request.POST)
        if form.is_valid():
            form.save()
            health_worker = form.cleaned_data.get("name")
            messages.success(
                request, f"Health Worker {health_worker} was created")
            return redirect("health_workers")

    return render(request, "sample_volumes/health_worker_form.html", context)


def createCourier(request):
    form = CourierForm()
    action = ACTIONS[0][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = CourierForm(request.POST)
        if form.is_valid():
            form.save()
            courier = form.cleaned_data.get("name")
            messages.success(request, f"Courier {courier} was created")
            return redirect("couriers")

    return render(request, "sample_volumes/courier_form.html", context)


def updateCourier(request, pk):
    courier = Courier.objects.get(id=pk)
    form = CourierForm(instance=courier)
    action = ACTIONS[1][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = CourierForm(request.POST, instance=courier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Courier {courier.name} was updated")
            return redirect("couriers")

    return render(request, "sample_volumes/courier_form.html", context)


def deleteCourier(request, pk):
    courier = Courier.objects.get(id=pk)
    if request.method == "POST":
        courier.delete()
        messages.success(
            request, f"Courier {courier.name} was deleted")
        return redirect("couriers")
    context = {"item": courier}
    return render(request, "sample_volumes/delete.html", context)


def updateHealth_Worker(request, pk):
    health_worker = Health_Worker.objects.get(id=pk)
    form = Health_WorkerForm(instance=health_worker)
    action = ACTIONS[1][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = Health_WorkerForm(request.POST, instance=health_worker)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Health worker {health_worker.name} was updated")
            return redirect("health_workers")

    return render(request, "sample_volumes/health_worker_form.html", context)


def deleteHealth_Worker(request, pk):
    health_worker = Health_Worker.objects.get(id=pk)
    if request.method == "POST":
        health_worker.delete()
        messages.success(
            request, f"Health worker {health_worker.name} was deleted")
        return redirect("health_workers")
    context = {"item": health_worker}
    return render(request, "sample_volumes/delete.html", context)


def makeRoutes(request, pk=""):
    context = {}
    districts = District.objects.order_by("name")
    date_list = []
    route_date = ""
    future_date = False

    route_status = {
        "status": "not_published",
        "badge_color": "danger",
        "display_text": "Not Saved",
        "button_text": "Save Routes",
    }

    for i in range(0, 7):
        date_list.append(
            {
                "index": i,
                "date": (datetime.now() - timedelta(days=i)),
                "date_string": (datetime.now() - timedelta(days=i)).strftime(
                    "%a-%d-%b"
                ),
            }
        )

    date_list.reverse()

    facilities = ""

    selected_district = ""
    courier_count = 0

    if request.method == "POST":
        if "date" in request.POST:
            route_date = datetime.strptime(request.POST["date"], "%Y-%m-%d")
        if "district" in request.POST:
            # if you have selected a district show information on when route was saved
            selected_district = districts.get(id=request.POST["district"])
            routes_for_selected_date = Route.objects.filter(
                district=selected_district.id, route_date=route_date
            ).order_by("-created_at")
            # if the route has been created
            if routes_for_selected_date.count() > 0:
                tr = routes_for_selected_date.first()
                route_created_by = tr.created_by
                route_created_at = tr.created_at
                route_created_at = route_created_at.strftime(
                    "%a, %d %b %I:%M %p")
                route_status["status"] = "published"
                route_status["badge_color"] = "success"
                route_status[
                    "display_text"
                ] = f"Saved on {route_created_at} by {route_created_by}"
                route_status["button_text"] = "Update Routes"

        # When you click save or update routes check if all
        if all(
            params in request.POST
            for params in ("routes", "selected_district", "courier_count", "selected_date")
        ):
            routes = json.loads(request.POST["routes"])
            selected_district = json.loads(request.POST["selected_district"])
            courier_count = json.loads(request.POST["courier_count"])
            user_id = json.loads(request.POST["user_id"])
            route_date = json.loads(request.POST["selected_date"])
            route_date = datetime.strptime(
                route_date[1:11].replace('"', ""), "%Y-%m-%d")
            created_routes = []
            updated = True

            selected_district = District.objects.get(id=selected_district)
            route_number = 1
            for route in routes:
                # Check if route exists or a new one is being created.
                created_route = Route.objects.filter(
                    district=selected_district,
                    route_date=route_date,
                    route_number=route_number,
                ).first()
                if created_route is None:
                    created_route = Route(
                        route_number=route_number,
                        route_date=route_date,
                        district=selected_district,
                        created_by=User.objects.get(id=user_id),
                    )
                    created_route.save()
                    updated = False

                created_route.facilities.set(
                    Facility.objects.filter(id__in=route["facilities"]),
                    through_defaults={"created": datetime.now()},
                )
                created_route.save()

                created_routes.append(model_to_dict(created_route))
                route_number += 1
            success, message = main(created_routes, updated)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse(
                    {"created_routes": "created successfully"}, status=200
                )

            print("Hello")

    if selected_district:
        context.update({"selected_district": selected_district})
        facilities = Facility.objects.filter(district=selected_district.id)
        courier_count = Courier.objects.filter(
            district=selected_district.id).count()

    if route_date:
        future_date = route_date.date() >= date.today()

    context.update(
        {
            "districts": districts,
            "selected_date": route_date,
            "future_date": future_date,
            "route_status": route_status,
            "facilities": facilities,
            "date_list": date_list,
            "courier_count": range(courier_count),
        }
    )

    return render(request, "sample_volumes/make_routes.html", context)


def viewRoutes(request):
    routes = []
    districts = District.objects.order_by("name")
    route_date = date.today() + timedelta(days=1)

    if request.method == "POST":
        if "date" in request.POST:
            route_date = request.POST["date"]
            route_date = datetime.strptime(route_date, "%Y-%m-%d")

    for district in districts:
        num_of_couriers = District.objects.get(
            id=district.id).courier_set.count()
        district_routes = Route.objects.filter(
            district=district.id, route_date=route_date
        ).order_by("-created_at")[:num_of_couriers]
        routes += district_routes

    context = {"routes": routes, "selected_date": route_date}
    return render(request, "sample_volumes/routes.html", context)


def facilityGroups(request):
    facility_groups = FacilityGroup.objects.all()
    context = {"facility_groups": facility_groups}
    return render(request, "sample_volumes/facility_groups.html", context)


def createFacilityGroup(request):
    form = FacilityGroupForm
    action = ACTIONS[0][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = FacilityGroupForm(request.POST)
        if form.is_valid():
            form.save()
            facility_group = form.cleaned_data.get("name")
            messages.success(request, f"Facility {facility_group} was created")
            return redirect("facility_groups")

    return render(request, "sample_volumes/facility_group_form.html", context)


def daily_sample_report(request):
    data = {}
    context = {}
    districts = District.objects.order_by("name")

    if request.method == "POST":
        date = request.POST["date"]
        district = request.POST["district"]

        if date and district:
            date = datetime.strptime(date, "%Y-%m-%d")
            district = District.objects.get(id=district)

            facilities = Facility.objects.filter(
                district=district).order_by("name")
            facility_count = facilities.count()

            for facility in facilities:
                data[facility.name] = facility.get_daily_sample_volumes(
                    format="types", selected_date=date
                )
                data[facility.name]["code"] = facility.facility_code

        context.update({"date": date, "district": district, "data": data})
        template_path = "sample_volumes/daily_report_template.html"
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type="application/pdf")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{district.name}_USSD_{date.strftime("%Y-%m-%d")}_report.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(
            html,
            dest=response,
        )

        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>")
        return response

    context.update({"districts": districts})
    return render(request, "sample_volumes/daily_report.html", context)


def facilityGroupFacilities(request, pk):

    context = {}
    fg = FacilityGroup.objects.get(id=pk)
    fg_facilities = fg.facility_set.values_list("id", flat=True)
    fg_facilities = list(fg_facilities)
    facilities_list = Facility.objects.filter(district=fg.district)
    facilities_list = facilities_list.filter(
        Q(facility_group=None) | Q(facility_group=fg)
    )
    context.update(
        {
            "facility_group": fg,
            "fg_facilities": fg_facilities,
            "facilities_list": facilities_list,
        }
    )

    removed = []
    added = []

    if request.method == "POST":
        submitted_facilities = request.POST.getlist("facilities[]")
        submitted_facilities = list(map(int, submitted_facilities))

        for item in fg_facilities:
            if int(item) not in submitted_facilities:
                removed.append(item)

        for item in submitted_facilities:
            if int(item) not in fg_facilities:
                added.append(item)

        if len(added) > 0:
            for a_facility in added:
                f = Facility.objects.get(id=a_facility)
                f.facility_group = fg
                f.save()

        if len(removed) > 0:
            for r_facility in removed:
                f = Facility.objects.get(id=r_facility)
                f.facility_group = None
                f.save()

        return redirect("home")

    return render(request, "sample_volumes/facility_group_members.html", context)


def daily_courier_report(request):
    # Model data
    data = {}
    context = {}
    districts = District.objects.order_by("name")
    assignments = []

    if request.method == "POST":
        date = request.POST["date"]
        district = request.POST["district"]

        if date and district:
            date = datetime.strptime(date, "%Y-%m-%d")
            district = District.objects.get(id=district)
            route_assignments = Courier.get_route_assignments(date, district)

            # get the list of facilities in the routes and compare with trips
            # for each courier check if one of his visited facilities for the day has a facility in the routes for the day

            for facility in facilities:
                data[facility.name] = facility.get_daily_sample_volumes(
                    format="types", selected_date=date
                )
                data[facility.name]["code"] = facility.facility_code

            context.update(
                {
                    "date": date,
                    "district": district,
                    "data": data,
                    "generated_time": datetime.now(),
                }
            )

        # Rendered
        html_string = render_to_string(
            "sample_volumes/courier_report_template.html", context
        )
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        result = html.write_pdf()

        response = HttpResponse(result, content_type="application/pdf")
        response["Content-Disposition"] = 'filename="home_page.pdf"'
        return response

    context.update({"districts": districts})
    return render(request, "sample_volumes/daily_courier_report.html", context)


def report_design(request):
    context = {}
    date = ""
    district = ""
    couriers = ""

    generated_time = datetime.now()
    if request.method == "POST":
        date = request.POST["date"]
        district = request.POST["district"]

        date = datetime.strptime(date, "%Y-%m-%d")
        district = District.objects.get(id=district)
        couriers = Courier.objects.filter(district=district).order_by('name')
        route_assignments = Courier.get_route_assignments(date, district)

        context.update({
            "date": date,
            "district": district,
            "generated_time": generated_time,
            "couriers": couriers,
            "route_assignments": route_assignments
        })

        # Rendered
        html_string = render_to_string(
            'sample_volumes/report_design.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        result = html.write_pdf()

        response = HttpResponse(result, content_type="application/pdf")
        response["Content-Disposition"] = 'filename="home_page.pdf"'
        return response

    # return render(request, "sample_volumes/report_design.html", context)


def updateFacilityGroup(request, pk):
    facility_group = FacilityGroup.objects.get(id=pk)
    form = FacilityGroupForm(instance=facility_group)
    action = ACTIONS[1][1]
    context = {"form": form, "action": action}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = FacilityGroupForm(request.POST, instance=facility_group)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Facility group {facility_group.name} was updated")
            return redirect("facility_groups")

    return render(request, "sample_volumes/facility_group_form.html", context)


def deleteFacilityGroup(request, pk):
    facility_group = FacilityGroup.objects.get(id=pk)
    if request.method == "POST":
        facility_group.delete()
        messages.success(
            request, f"Facility group {facility_group.name} was deleted")
        return redirect("facility_groups")
    context = {"item": facility_group}
    return render(request, "sample_volumes/delete.html", context)


def users(request):
    users = User.objects.all()
    context = {"users": users}
    return render(request, "sample_volumes/users.html", context)


def deleteUser(request, pk):
    # facility_group = FacilityGroup.objects.get(id=pk)
    # if request.method == "POST":
    #     facility_group.delete()
    #     messages.success(
    #         request, f"Facility group {facility_group.name} was deleted")
    #     return redirect("facility_groups")
    # context = {"item": facility_group}
    # return render(request, "sample_volumes/delete.html", context)
    pass


def updateUser(request, pk):
    # facility_group = FacilityGroup.objects.get(id=pk)
    # form = FacilityGroupForm(instance=facility_group)
    # action = ACTIONS[1][1]
    # context = {"form": form, "action": action}

    # if request.method == "POST":
    #     # print('Printing POST: ', request.POST)
    #     form = FacilityGroupForm(request.POST, instance=facility_group)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(
    #             request, f"Facility group {facility_group.name} was updated")
    #         return redirect("facility_groups")

    # return render(request, "sample_volumes/facility_group_form.html", context)
    pass


def resetPassword(request, pk):
    user = User.objects.get(id=pk)
    form = PasswordResetCustomForm(instance=user)
    action = ACTIONS[3][1]
    context = {"form": form, "action": action, "user": user}

    if request.method == "POST":
        # print('Printing POST: ', request.POST)
        form = PasswordResetCustomForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"User password for {user.get_full_name} was updated")
            return redirect("users")

    return render(request, "sample_volumes/reset_password.html", context)

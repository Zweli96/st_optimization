from django.contrib.auth.models import User
from django.db import models
from datetime import date, datetime, timedelta
from phonenumber_field.modelfields import PhoneNumberField
import uuid


# Create your models here.

STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("DELETED", "DELETED"),
)

FACILITY_OPERATOR = (
    ("Malawi Government", "Malawi Government"),
    ("CHAM", "CHAM"),
    ("Private", "Private"),
)

FACILITY_TYPE = (
    ("Health Centre", "Health Centre"),
    ("District Hospital", "District Hospital"),
    ("Clinic", "Clinic"),
    ("Rural Community Hospital", "Rural Community Hospital"),
    ("Central Hospital", "Central Hospital"),
)

SAMPLE_TYPE = (
    ("1", "VL"),
    ("2", "EID"),
    ("3", "TB"),
    ("4", "Other"),
)

DISTRICT_REGIONS = (
    ("Northern Region", "Northern Region"),
    ("Southern Region", "Southern Region"),
    ("Central Region", "Central Region"),
)


class District(models.Model):
    name = models.CharField(max_length=200)
    region = models.CharField(choices=DISTRICT_REGIONS, max_length=200)
    commcare_district_group_id = models.CharField(
        max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name


class FacilityGroup(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, unique=True)
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name

    def get_facilities(self):
        facilities_string = ""
        list_of_facilities = self.facility_set.all()
        if list_of_facilities:
            for facility in list_of_facilities:
                facilities_string += f"{facility.name}, "

        if facilities_string:
            facilities_string = facilities_string[:-2]
        else:
            facilities_string = "Empty"

        return facilities_string


class Facility(models.Model):
    name = models.CharField(max_length=200)
    commcare_name = models.CharField(max_length=200, blank=True, null=True)
    district = models.ForeignKey(
        District, null=True, on_delete=models.SET_NULL)
    facility_code = models.CharField(
        max_length=200, blank=True, null=True, unique=True)
    operator = models.CharField(
        max_length=200, choices=FACILITY_OPERATOR, blank=True, null=True
    )
    facility_group = models.ForeignKey(
        FacilityGroup, on_delete=models.SET_NULL, blank=True, null=True
    )
    facility_type = models.CharField(
        max_length=200, choices=FACILITY_TYPE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name

    def get_daily_sample_volumes(self, format="string", selected_date=None):
        incorrectly_reported = {}

        volumes = {}
        volume_string = ""
        total_volumes = 0

        if selected_date is None:
            selected_date = datetime.now()
        today = selected_date

        # samples = self.sample_volumes_set.all()

        samples = self.sample_volumes_set.filter(
            reported_date__year=today.year,
            reported_date__month=today.month,
            reported_date__day=today.day,
        )
        # reported_date__year=2021, reported_date__month=12, reported_date__day=6

        if samples.count() == 0 and format != "types":
            return "not yet reported"

        for s in SAMPLE_TYPE:
            # Get the most recently reported sample on that day
            sample = samples.filter(sample_type=s[0]).order_by(
                "-reported_date").first()

            if sample:
                # VL = the volume in the volumes dictionary
                volumes[s[1]] = sample.volume
                total_volumes += sample.volume

                # incorect_sample = sample.check_if_correct()
                # if incorect_samples:
                #     incorrectly_reported.update({self.id: []})
                #     incorrectly_reported[self.id].append(incorrect_sample)

            else:
                volumes[s[1]] = "NA"

        for key, value in volumes.items():
            volume_string += f"{value}_"

        volume_string = volume_string[:-1]
        if format == "string":
            return volume_string
        elif format == "types":
            return volumes
        elif format == "total":
            return

        # return samples
        # for sample in samples:
        #     return sample.volume

    def get_last_reported(self):
        recent_sample = self.sample_volumes_set.all().order_by("-reported_date").first()
        if recent_sample:
            return recent_sample.reported_date
        else:
            return "NA"

    def get_last_visit(self):
        recent_visit = self.visit_set.all().order_by("-visit_date").first()
        if recent_visit:
            return recent_visit.visit_date
        else:
            return "NA"

    def get_last_reporter(self, selected_date):
        recent_sample = ""
        reporting_info = {}
        reported = "no"
        reported_at = ""
        reported_by = ""
        on_time = "no"
        text = ""
        on_time_reported = datetime.now().replace(
            hour=14, minute=0, second=0, microsecond=0)

        todays_sample = self.sample_volumes_set.all().filter(reported_date__year=selected_date.year,
                                                             reported_date__month=selected_date.month,
                                                             reported_date__day=selected_date.day).first()
        # Reported date check
        if todays_sample:
            reported = "yes"
            # on time check
            if todays_sample.reported_date.time() < on_time_reported.time():
                on_time = "yes"
            # who reported and when
            reported_by, reported_at = todays_sample.reporter()

        else:
            recent_sample = self.sample_volumes_set.all().order_by("-reported_date").first()
            if recent_sample:
                # who reported and when
                reported_by, reported_at = recent_sample.reporter()

        if not recent_sample and not todays_sample:
            text = "Facility has never reported"
        else:
            text = f'Last reported by {reported_by} on {reported_at}'

        reporting_info.update({
            "reported": reported,
            "on_time": on_time,
            "text": text
        })

        return reporting_info

    def days_since_last_visit(self):
        recent_visit = self.get_last_visit()
        if recent_visit != "NA":
            days_since = date.today() - recent_visit
            return days_since.days
        else:
            return "NA"

    def check_scheduled(self, route):
        if self in route.facilities.all():
            return "yes"
        else:
            return "no"

    def check_trip_logged(self, courier, trip_date):
        trip_facilites = Trip.objects.filter(courier=courier, trip_date__year=trip_date.year,
                                             trip_date__month=trip_date.month, trip_date__day=trip_date.day).values_list('end_location', flat=True)

        if self.id in trip_facilites:
            return "yes"
        else:
            return "no"

    def check_visit_logged(self, courier, visit_date):
        visit_facilites = Visit.objects.filter(courier=courier, visit_date__year=visit_date.year,
                                               visit_date__month=visit_date.month, visit_date__day=visit_date.day).values_list('facility', flat=True)

        if self.id in visit_facilites:
            return "yes"
        else:
            return "no"

    def get_previously_reported_volumes(facility, reported_date, sample_type):
        # Yesterdays date
        # facility = Facility.objects.get(id=facility)
        reported_date = reported_date - timedelta(days=1)
        sample_type = int(sample_type)
        samples = facility.sample_volumes_set.filter(
            reported_date__year=reported_date.year,
            reported_date__month=reported_date.month,
            reported_date__day=reported_date.day,
        )

        sample = samples.filter(sample_type=sample_type).order_by(
            "-reported_date").first()

        if sample:
            return sample.volume
        else:
            return 'NA'


class SampleType(models.Model):
    sample_type = models.CharField(max_length=200, null=True)
    sample_type_long = models.CharField(max_length=200, null=True)
    sample_code = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.sample_type


class Sample_Volumes(models.Model):
    facility = models.ForeignKey(
        Facility, null=True, on_delete=models.SET_NULL)
    sample_type = models.ForeignKey(
        SampleType, null=True, on_delete=models.SET_NULL)
    volume = models.IntegerField(default=0)
    reported_date = models.DateTimeField(null=True)
    session_id = models.IntegerField(default=0)
    reported_by = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateTimeField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return f'{self.facility.district}_{self.facility}_{self.sample_type}_{self.reported_date.strftime("%d-%m-%Y")}'

    def reporter(self):
        '''
        Returns name, number of the reporter and date when the sample was reported
        '''
        reporter = ""
        phonenumber = self.reported_by.replace("+", "")
        phonenumber = int(float(phonenumber))
        phonenumber = "+" + str(phonenumber)

        try:
            reporter = Health_Worker.objects.get(phone_number=phonenumber)
        except:
            pass

        if not reporter:
            reporter = self.reported_by
        else:
            reporter = f'{reporter.name} ({reporter.phone_number})'

        return (reporter, self.reported_date.strftime("%a %d-%b @%H:%M"))

    def check_if_correct(self, reported_date):
        # Check when it was last reported
        facility = self.facility
        previous_sample = facility.sample_volumes_set.filter(
            sample_type=self.sample_type, reported_date__lt=reported_date).order_by("-reported_date").first()
        if self.volume < previous_sample.volume:
            last_visit = facility.get_last_visit()
            if isinstance(facility.get_last_visit, date):
                if last_visit < previous_sample.reported_date.date():
                    return {"sample_type": self.sample_type, "previous_volume": previous_sample.volume, "last_reported_date": previous_sample.reported_date}

        # reported
        pass

class DataUpdates(models.Model):
    time_started = models.DateTimeField(auto_now_add=True)
    time_completed = models.DateTimeField(null=True)
    completed = models.BooleanField(null=True, default=False)
    user = models.CharField(null=True,max_length=200)


class Health_Worker(models.Model):
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    phone_number = PhoneNumberField()
    facility = models.ForeignKey(Facility, models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name


class Courier(models.Model):
    name = models.CharField(max_length=200)
    phone_number = PhoneNumberField()
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    commcare_user_name = models.CharField(max_length=200)
    commcare_user_id = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name

    # Based on the courier trips assign them to the route that matches their trip
    def get_route_assignments(route_date, district):
        assignments = {}

        routes = Route.objects.filter(
            route_date=route_date, district=district
        ).prefetch_related("facilities")

        couriers = Courier.objects.filter(district=district)

        if routes:
            for courier in couriers:
                trip_logged_facilities = Trip.objects.filter(
                    courier=courier, trip_date=route_date
                ).values_list("end_location", flat=True)
                visit_logged_facilities = Visit.objects.filter(
                    courier=courier, visit_date=route_date
                ).values_list("facility", flat=True)
                if trip_logged_facilities or visit_logged_facilities:
                    for route in routes:
                        matched_facilities = list(
                            set(route.facilities.all().values_list('id', flat=True)) & (
                                set(trip_logged_facilities) | set(visit_logged_facilities))
                        )
                        if matched_facilities:
                            # assignments.append((courier, route))
                            assignments.update({courier.id: route})
                            routes = routes.exclude(id=route.id)
                            couriers = couriers.exclude(id=courier.id)
                            break
            for courier, route in zip(couriers, routes):
                assignments.update({courier.id: route})
        else:
            for courier in couriers:
                assignments.update({courier.id: None})
        return assignments


def tomorrows_date():
    return datetime.now() + timedelta(days=1)


class Route(models.Model):
    route_number = models.IntegerField()
    route_date = models.DateTimeField(default=tomorrows_date)
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    facilities = models.ManyToManyField(Facility, through="RouteFacility")
    confirmed = models.CharField(max_length=10, default="no")
    confirmed_time = models.DateTimeField(null=True)
    added_facilities = models.CharField(max_length=1000, null=True)
    rider = models.ForeignKey(Courier, models.SET_NULL, null=True)
    reason_for_adding_facilities = models.CharField(max_length=1000, null=True)
    commcare_id = models.CharField(max_length=200, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def get_facilities(self):
        facilities_string = ""
        list_of_facilities = ""
        try:
            list_of_facilities = self.facilities.all()
        except:
            pass

        if list_of_facilities:
            for facility in list_of_facilities:
                facilities_string += f"{facility.name}, "
        else:
            facilities_string = "On Call"

        if facilities_string != "On Call":
            facilities_string = facilities_string[:-2]

        return facilities_string

    # Returns list of facilities with information on whether they were scheduled for that day or logged
    # Used in the courier report
    def get_courier_overview(courier, route, route_date):
        facilities = []  # final list
        route_facilities = []  # list with scheduled facilities for that route
        # list with scheduled facilities and not scheduled facilities
        consolidated_facilities = []

        scheduled = ""  # is the facility part of the route
        trip_logged = ""  # was the trip logged in commcare
        visit_logged = ""  # was the visit logged in commcare

        if route:
            route_facilities = list(
                route.facilities.all().values_list('id', flat=True))
        trip_facilities = list(Trip.objects.filter(courier=courier, trip_date__year=route_date.year,
                                                   trip_date__month=route_date.month, trip_date__day=route_date.day).values_list('end_location', flat=True))

        visit_facilities = list(Visit.objects.filter(courier=courier, visit_date__year=route_date.year,
                                                     visit_date__month=route_date.month, visit_date__day=route_date.day).values_list('facility', flat=True))

        trip_only_facilities = [
            x for x in trip_facilities if x not in route_facilities and x not in visit_facilities]

        visit_only_facilities = [
            x for x in visit_facilities if x not in route_facilities and x not in trip_facilities]

        consolidated_facilities.extend(route_facilities)
        consolidated_facilities.extend(trip_only_facilities)
        consolidated_facilities.extend(visit_only_facilities)

        for facility in consolidated_facilities:
            scheduled = "no"
            trip_logged = "no"
            visit_logged = "no"

            facility = Facility.objects.get(id=facility)
            if route:
                scheduled = facility.check_scheduled(route)
            trip_logged = facility.check_trip_logged(courier, route_date)
            visit_logged = facility.check_visit_logged(courier, route_date)

            facilities.append({"facility": facility, "scheduled": scheduled,
                              "trip_logged": trip_logged, "visit_logged": visit_logged})

        return facilities


class RouteFacility(models.Model):
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ("created",)


class Visit(models.Model):
    visit_id = models.CharField(max_length=200, unique=True)
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True)
    visit_date = models.DateField()
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    sample_volumes = models.JSONField(null=True)
    results = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)


class Trip(models.Model):
    trip_id = models.CharField(max_length=200)
    start_location = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True, related_name="start_locations"
    )
    end_location = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True, related_name="end_locations"
    )
    trip_date = models.DateField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    start_km = models.IntegerField(null=True)
    end_km = models.IntegerField(null=True)
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL
    )
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

from django.contrib.auth.models import User
from django.db import models
from datetime import date, datetime, timedelta
from phonenumber_field.modelfields import PhoneNumberField
import uuid


# Create your models here.

STATUS = (
    ('ACTIVE', 'ACTIVE'),
    ('DELETED', 'DELETED'),
)

FACILITY_OPERATOR = (
    ('Malawi Government', 'Malawi Government'),
    ('CHAM', 'CHAM'),
    ('Private', 'Private'),
)

FACILITY_TYPE = (
    ('Health Centre', 'Health Centre'),
    ('District Hospital', 'District Hospital'),
    ('Clinic', 'Clinic'),
    ('Rural Community Hospital', 'Rural Community Hospital'),
    ('Central Hospital', 'Central Hospital'),
)

SAMPLE_TYPE = (
    ('1', 'VL'),
    ('2', 'EID'),
    ('3', 'TB'),
    ('4', 'Other'),
)

DISTRICT_REGIONS = (
    ('Northern Region', 'Northern Region'),
    ('Southern Region', 'Southern Region'),
    ('Central Region', 'Central Region'),
)


class District(models.Model):
    name = models.CharField(max_length=200)
    region = models.CharField(choices=DISTRICT_REGIONS, max_length=200)
    commcare_district_group_id = models.CharField(
        max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
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
        User, blank=True, null=True, on_delete=models.SET_NULL)
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
                facilities_string += f'{facility.name}, '

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
        max_length=200, choices=FACILITY_OPERATOR, blank=True, null=True)
    facility_group = models.ForeignKey(
        FacilityGroup, on_delete=models.SET_NULL, blank=True, null=True)
    facility_type = models.CharField(
        max_length=200, choices=FACILITY_TYPE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name

    def get_daily_sample_volumes(self, format='string', selected_date=None):
        # today = date.today()
        if selected_date is None:
            selected_date = datetime.now()
        today = selected_date

        # samples = self.sample_volumes_set.all()

        samples = self.sample_volumes_set.filter(
            reported_date__year=today.year, reported_date__month=today.month, reported_date__day=today.day)
        # reported_date__year=2021, reported_date__month=12, reported_date__day=6

        if samples.count() == 0 and format != 'types':
            return 'not yet reported'

        volumes = {}
        volume_string = ""
        total_volumes = 0

        for s in SAMPLE_TYPE:
            # Get the most recently reported sample on that day
            sample = samples.filter(sample_type=s[0]).order_by(
                '-reported_date').first()

            if sample:
                # VL = the volume in the volumes dictionary
                volumes[s[1]] = sample.volume
                total_volumes += sample.volume
            else:
                volumes[s[1]] = 'NA'

        for key, value in volumes.items():
            volume_string += f'{value}_'

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
        recent_sample = self.sample_volumes_set.all().order_by('-reported_date').first()
        if recent_sample:
            return recent_sample.reported_date.strftime("%a %d-%b")
        else:
            return "NA"

    def get_last_visit(self):
        recent_visit = self.visit_set.all().order_by('-visit_date').first()
        if recent_visit:
            return recent_visit.visit_date.strftime("%a %d-%b")
        else:
            return "NA"


class SampleType(models.Model):
    sample_type = models.CharField(max_length=200, null=True)
    sample_type_long = models.CharField(max_length=200, null=True)
    sample_code = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
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
    reported_by = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
    edited_at = models.DateTimeField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return f'{self.facility.district}_{self.facility}_{self.sample_type}_{self.reported_date.strftime("%d-%m-%Y")}'


class Health_Worker(models.Model):
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    phone_number = PhoneNumberField()
    facility = models.ForeignKey(Facility, models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
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
        User, blank=True, null=True, on_delete=models.SET_NULL)
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name


# class Routes(models.Model):
#     route = ArrayField(base_field=models.CharField(max_length=200))
#     phone_number = models.IntegerField()
#     district = models.ForeignKey(District, models.SET_NULL, null=True)
#     commcare_id = models.CharField(max_length=200)


# class Results(models.Model):
#     name = models.CharField(max_length=200)
#     district = models.CharField(max_length=200, blank=True)
#     facility_code = models.CharField(max_length=200)
#     #operator = models.ManyToManyField()
#     #programs = models.ManyToManyField()
#     #facility_types = models.ManyToManyField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     #created_by = models.ForeignKey(to, on_delete)
#     edited_at = models.DateField(auto_now=True)
#     #edited_by = models.ForeignKey(to, on_delete)
#     #deleted_at = models.DateTimeField(blank=True, null=True)
#     #deleted_by = models.ForeignKey(to, on_delete)
#     status = models.CharField(choices=STATUS)

def tomorrows_date():
    return datetime.now() + timedelta(days=1)


class Route(models.Model):
    route_number = models.IntegerField()
    route_date = models.DateTimeField(default=tomorrows_date)
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    facilities = models.ManyToManyField(Facility, through='RouteFacility')
    confirmed = models.CharField(max_length=10, default='no')
    confirmed_time = models.DateTimeField(null=True)
    added_facilities = models.CharField(max_length=1000, null=True)
    rider = models.ForeignKey(Courier, models.SET_NULL, null=True)
    reason_for_adding_facilities = models.CharField(max_length=1000, null=True)
    commcare_id = models.CharField(max_length=200, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def get_facilities(self):
        facilities_string = ""
        list_of_facilities = self.facilities.all()

        if list_of_facilities:
            for facility in list_of_facilities:
                facilities_string += f'{facility.name}, '
        else:
            facilities_string = "On Call"

        if facilities_string != "On Call":
            facilities_string = facilities_string[:-2]

        return facilities_string


class RouteFacility(models.Model):
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ('created',)


class Visit(models.Model):
    visit_id = models.CharField(max_length=200, unique=True)
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True)
    visit_date = models.DateField()
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    sample_volumes = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)


class Trip(models.Model):
    trip_id = models.CharField(max_length=200)
    facility = models.ForeignKey(
        Facility, on_delete=models.SET_NULL, null=True)
    trip_date = models.DateTimeField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    start_km = models.IntegerField(null=True)
    end_km = models.IntegerField(null=True)
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, blank=True, null=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)


# class Visits(models.Model):
#     name = models.CharField(max_length=200)
#     district = models.CharField(max_length=200, blank=True)
#     facility_code = models.CharField(max_length=200)
#     #operator = models.ManyToManyField()
#     #programs = models.ManyToManyField()
#     #facility_types = models.ManyToManyField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     #created_by = models.ForeignKey(to, on_delete)
#     edited_at = models.DateField(auto_now=True)
#     #edited_by = models.ForeignKey(to, on_delete)
#     #deleted_at = models.DateTimeField(blank=True, null=True)
#     #deleted_by = models.ForeignKey(to, on_delete)
#     status = models.CharField(choices=STATUS)

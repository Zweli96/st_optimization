from django.contrib.auth.models import User
from django.db import models
from datetime import date, datetime
from phonenumber_field.modelfields import PhoneNumberField


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
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, null=True, blank=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name


class Facility(models.Model):
    name = models.CharField(max_length=200, null=True)
    district = models.ForeignKey(
        District, null=True, on_delete=models.SET_NULL)
    facility_code = models.CharField(max_length=200, null=True, unique=True)
    operator = models.CharField(
        max_length=200, choices=FACILITY_OPERATOR, null=True)
    facility_type = models.CharField(
        max_length=200, choices=FACILITY_TYPE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    # edited_at = models.DateField(auto_now=True, null=True)
    # edited_by = models.ForeignKey(
    #     User, null=True, blank=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete, null=True)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name

    def get_daily_sample_volumes(self, format='types'):
        # today = date.today()
        today = date(2021, 12, 8)

        # samples = self.sample_volumes_set.all()

        samples = self.sample_volumes_set.filter(
            reported_date__year=today.year, reported_date__month=today.month, reported_date__day=today.day)
        # reported_date__year=2021, reported_date__month=12, reported_date__day=6

        if samples.count() == 0:
            return 'Not yet reported'

        volumes = {}
        volume_string = ""
        total_volumes = 0

        for s in SAMPLE_TYPE:
            sample = samples.filter(sample_type=s[0]).order_by(
                '-reported_date').first()

            if sample:
                volumes[s[1]] = sample.volume
                total_volumes += sample.volume
            else:
                volumes[s[1]] = 'NA'

        for key, value in volumes.items():
            volume_string += f'{key}: {value}, '

        volume_string = volume_string[:-2]
        if format == "types":
            return volume_string
        elif format == "total":
            return

        # return samples
        # for sample in samples:
        #     return sample.volume


class SampleType(models.Model):
    sample_type = models.CharField(max_length=200, null=True)
    sample_type_long = models.CharField(max_length=200, null=True)
    sample_code = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, null=True, blank=True, on_delete=models.SET_NULL)
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
    reported_by = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    edited_at = models.DateTimeField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, null=True, blank=True, on_delete=models.SET_NULL)
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
        User, null=True, blank=True, on_delete=models.SET_NULL)
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, null=True, blank=True, on_delete=models.SET_NULL)
    # deleted_at = models.DateTimeField(blank=True, null=True)
    # deleted_by = models.ForeignKey(to, on_delete)
    status = models.CharField(max_length=200, choices=STATUS, null=True)

    def __str__(self):
        return self.name


class Courier(models.Model):
    name = models.CharField(max_length=200)
    phone_number = PhoneNumberField()
    district = models.ForeignKey(District, models.SET_NULL, null=True)
    commcare_user_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL)
    edited_at = models.DateField(auto_now=True)
    # edited_by = models.ForeignKey(
    #     User, null=True, blank=True, on_delete=models.SET_NULL)
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


# class Routes(models.Model):
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

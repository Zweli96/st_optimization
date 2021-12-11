from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Facility)
admin.site.register(Sample_Volumes)
admin.site.register(SampleType)
admin.site.register(District)
admin.site.register(Health_Worker)
admin.site.register(Courier)

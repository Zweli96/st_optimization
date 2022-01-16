from django import template
register = template.Library()
    
from ..models import Facility
  
@register.simple_tag
def get_daily_volumes_from_facility(facility, types, date):
      return Facility.get_daily_sample_volumes(facility,types, date)
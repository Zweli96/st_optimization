from ..models import Facility, Route, Trip, Visit
from django import template
import json
register = template.Library()


@register.simple_tag
def get_daily_volumes_from_facility(facility, types, date):
    return Facility.get_daily_sample_volumes(facility, types, date)


@register.simple_tag
def get_courier_overview(courier, route, route_date):
    return Route.get_courier_overview(courier, route, route_date)


@register.simple_tag
def get_trips(courier, route_date):
    trip_facilities = Trip.objects.filter(courier=courier, trip_date__year=route_date.year,
                                          trip_date__month=route_date.month, trip_date__day=route_date.day)
    return trip_facilities


@register.simple_tag
def get_visits(courier, route_date):
    visit_facilities = Visit.objects.filter(courier=courier, visit_date__year=route_date.year,
                                            visit_date__month=route_date.month, visit_date__day=route_date.day)
    return visit_facilities

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def get_route_facilities(route):
    return Route.get_facilities(route)

@register.simple_tag
def get_courier_overview(courier, route, route_date):
    return Route.get_courier_overview(courier, route, route_date)

@register.filter
def jsonify(data):
    if isinstance(data, dict):
        return data
    else:
        return json.loads(data)

@register.simple_tag
def get_previously_reported_volume(facility, date, sample_type):
    return Facility.get_previously_reported_volumes(facility,date, sample_type)

@register.simple_tag
def get_last_reporter(facility, date):
    return Facility.get_last_reporter(facility, date)
from django.conf import settings
from django.core.mail import EmailMessage
# from weasyprint import HTML
from django.template.loader import render_to_string
import os
from .models import (
    District,
    Courier,
)
from datetime import datetime
from django.contrib.auth.models import User


def courier_report(selected_date, district):
    context = {}
    generated_time = datetime.now()
    
    date = datetime.strptime(selected_date, "%Y-%m-%d")
    district = District.objects.get(id=district.id)
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

    HOST = "http://localhost:8000/static/"

    # html = HTML(string=html_string, base_url=HOST)
    # pdf = html.write_pdf()

    # return pdf

    # return render(request, "sample_volumes/report_design.html", context)


def sendEmail(report_type):
    report_districts = District.objects.filter(optimization_district=True)
    emailing_list = User.objects.filter(email__isnull=False, username='zgolowa')
    emailing_list = [x.email for x in emailing_list]

    for district in report_districts:
       if(report_type == 'courier'):
           
            message = "Hello,\n\nThe attached document contains a summary of today's CommCare data entered by the RFH couriers in your district. Please check the data and discuss any errors with the couriers as soon as possible."
            report_date = datetime.now()
            report_date = report_date.strftime("%Y-%m-%d")
            pdf = courier_report(report_date, district)
            email = EmailMessage(
                f'{district.name} {report_type} reports {report_date}', message, 'R4H Optimization Reports', emailing_list)
            email.attach(f'{district.name}_{report_type}_reporting_{report_date}.pdf', pdf, "application/pdf")
            email.send()

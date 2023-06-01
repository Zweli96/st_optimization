import datetime


def get_weekdays(start_date, end_date):
    weekdays = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday (0 to 4)
            weekdays.append(current_date)
        current_date += datetime.timedelta(days=1)

    return weekdays

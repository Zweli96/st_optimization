from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dataUpdater import dataFetch
from dataUpdater.sms import send_sms
from dataUpdater.commcare import get_visits, get_trips
from sample_volumes.emails import sendEmail


def start():
    scheduler = BackgroundScheduler()
    # get_trips()
    # get_visits()
    # # sendEmail('courier')
    #dataFetch.updateData()
    scheduler.start()
    scheduler.add_job(dataFetch.updateData, "interval", minutes=15)
    scheduler.add_job(get_visits, "interval", minutes=40)
    scheduler.add_job(get_trips, "interval", minutes=40)
    scheduler.add_job(
        send_sms.send_sms_notifications, "cron", day_of_week="mon-fri", hour=8
    )
    scheduler.add_job(
        send_sms.send_sms_reminders, "cron", day_of_week="mon-fri", hour=14,
    )
    # print('No Import')

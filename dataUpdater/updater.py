from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dataUpdater import dataFetch
from dataUpdater.sms import send_sms


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(dataFetch.updateData, 'interval', minutes=10)
    scheduler.add_job(send_sms.send_sms_notifications, 'cron',
                      day_of_week='mon-fri', hour=8)
    scheduler.add_job(send_sms.send_sms_reminders, 'cron',
                      day_of_week='mon-fri', hour=14)
    scheduler.start()
    # dataFetch.updateData()
    # print('No Import')

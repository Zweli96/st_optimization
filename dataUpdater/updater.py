from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dataUpdater import dataFetch


def start():
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(dataFetch.updateData, 'interval', minutes=10)
    # scheduler.start()
    # dataFetch.updateData()
    print('start')

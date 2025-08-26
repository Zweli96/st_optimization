from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dataUpdater import dataFetch
from dataUpdater.sms import send_sms
from dataUpdater.commcare import get_visits, get_trips
import threading

# Create a lock for synchronizing data updates and reminders
data_lock = threading.Lock()


def safe_update_data():
    """Runs updateData inside a lock to prevent overlap."""
    with data_lock:
        dataFetch.updateData()


def send_reminders_with_fresh_data():
    """Updates data first, then sends reminders."""
    with data_lock:
        dataFetch.updateData()
        send_sms.send_sms_reminders()


def start():
    scheduler = BackgroundScheduler()

    # Initial run to ensure we start with fresh data
    scheduler.start()
    safe_update_data()

    # Regular updates (with lock)
    scheduler.add_job(safe_update_data, "interval",
                      minutes=15, max_instances=1)
    scheduler.add_job(get_visits, "interval", minutes=40)
    scheduler.add_job(get_trips, "interval", minutes=40)

    # Morning notifications (no lock needed, doesn't modify the data)
    scheduler.add_job(
        send_sms.send_sms_notifications, "cron", day_of_week="mon-fri", hour=8
    )

    # Afternoon reminders — runs update first, both inside lock
    scheduler.add_job(
        send_reminders_with_fresh_data, "cron", day_of_week="mon-fri", hour=14
    )

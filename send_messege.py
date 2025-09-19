from apscheduler.schedulers.background import BackgroundScheduler
import time
from send_alert_user import send_message_to_users
from send_Email_institution import send_message_to_all

def job1():
    send_message_to_users()

def job2():
    send_message_to_all()

scheduler = BackgroundScheduler()
scheduler.add_job(job1, 'interval', seconds=60)
scheduler.add_job(job2, 'interval', seconds=60)

scheduler.start()

# Keep the script running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()

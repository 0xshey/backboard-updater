from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess
import os

CWD = os.getcwd()
VENV_PATH = ".venv/bin/python"
current_env = os.environ.copy()

def run_update(update_type, date=None):
	command = ["python", "updater.py", "--type", update_type]
	if date:
		command.extend(["--date", date])
	try:
		subprocess.run(
			command,
			cwd=CWD,
			env=current_env,
			text=True,
			check=True
		)
	except subprocess.CalledProcessError as e:
		print(f"Error: {e}")
		return False
	return True

def do_daily_update():
	print("STARTING UPDATE (daily)")
	if run_update("games") and run_update("games", "tomorrow") and run_update("games", "yesterday"):
		print("UPDATE COMPLETE")
	else:
		print("UPDATE FAILED")

def do_live_update():
	print("STARTING UPDATE (live)")
	if run_update("games") and run_update("players"):
		print("UPDATE COMPLETE")
	else:
		print("UPDATE FAILED")

scheduler = BlockingScheduler()

# Schedule the live update to run every minute between 3PM and 12AM
scheduler.add_job(
	do_live_update,
	CronTrigger(minute="*", hour="10-23")
)

# Schedule the daily update to run at 4AM
scheduler.add_job(
	do_daily_update,
	CronTrigger(minute="19", hour="16")
)

def main():
	print("Scheduler started")
	try:
		scheduler.start()
	except subprocess.CalledProcessError as e:
		print(f"Command failed with return code {e.returncode}")
	except KeyboardInterrupt:
		print("Scheduler stopped")

if __name__ == "__main__":
	main()

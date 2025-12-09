import os
import sys
import subprocess
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.blocking import BlockingScheduler
import tzlocal


CWD = os.path.join(os.getcwd())
current_env = os.environ.copy()

def update_standings_job():
	command = [sys.executable, "update_standings.py"]
	# command = ["pwd"]
	try:
		subprocess.run(
			command,
			cwd=os.path.join(CWD, "src"),
			env=current_env,
			text=True,
			check=True
		)

	except subprocess.CalledProcessError as e:
		print(f"Error: {e}")
		return False

	return True

def update_games_job():
	command = [sys.executable, "update_games.py"]
	try:
		subprocess.run(
			command,
			cwd=os.path.join(CWD, "src"),
			env=current_env,
			text=True,
			check=True
		)

	except subprocess.CalledProcessError as e:
		print(f"Error: {e}")
		return False

	return True

def update_averages_job():
	command = [sys.executable, "update_averages.py"]
	try:
		subprocess.run(
			command,
			cwd=os.path.join(CWD, "src"),
			env=current_env,
			text=True,
			check=True
		)

	except subprocess.CalledProcessError as e:
		print(f"Error: {e}")
		return False

	return True

def main():
	print("Starting scheduler")
	print("Server timezone:", tzlocal.get_localzone())
	scheduler = BlockingScheduler()

	# # Schedule the standings update to run every hour
	# scheduler.add_job(
	# 	update_standings_job,
	# 	CronTrigger(minute="0", hour="*")
	# )

	# Schedule the games update to run every d`ay at 5AM
	scheduler.add_job(
		update_games_job,
		CronTrigger(minute="*")
	)

	scheduler.add_job(
		update_averages_job,
		CronTrigger(minute="0", hour="0,6,12,18")
	)

	try:
		scheduler.start()
	except subprocess.CalledProcessError as e:
		print(f"Command failed with return code {e.returncode}")
	except KeyboardInterrupt:
		print("Scheduler stopped")

	
if __name__ == "__main__":
	main()
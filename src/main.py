import os
import subprocess
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.blocking import BlockingScheduler

CWD = os.path.join(os.getcwd())
current_env = os.environ.copy()

def update_standings_job():
	command = ["python", "update_standings.py"]
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
	command = ["python", "update_games.py"]
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
	command = ["python", "update_averages.py"]
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
	scheduler = BlockingScheduler()

	# # Schedule the standings update to run every hour
	# scheduler.add_job(
	# 	update_standings_job,
	# 	CronTrigger(minute="0", hour="*")
	# )

	# Schedule the games update to run every d`ay at 5AM
	scheduler.add_job(
		update_games_job,
		CronTrigger(minute="*", hour="12-23")
	)

	# scheduler.add_job(
	# 	update_averages_job,
	# 	CronTrigger(minute="0", hour="1")
	# )

	try:
		scheduler.start()
	except subprocess.CalledProcessError as e:
		print(f"Command failed with return code {e.returncode}")
	except KeyboardInterrupt:
		print("Scheduler stopped")

	
if __name__ == "__main__":
	main()
import sys
from lib.logger import logging
from lib.supabase import supabase
from app.fetchers import get_schedule
from app.parsers import parse_schedule

logger = logging.getLogger("backboard-logger")

def update_schedule_task():
	logger.info("Starting update for schedule")
	
	# Fetch
	logger.debug("Fetching schedule...")
	schedule_res = get_schedule()
	if not schedule_res:
		logger.error("Failed to fetch schedule")
		return

	# Parse
	try:
		games, game_teams = parse_schedule(schedule_res)
		logger.info(f"Parsed {len(games)} games and {len(game_teams)} game teams")
	except Exception as e:
		logger.error(f"Failed to parse schedule: {e}")
		return

	# Upsert Games
	if games:
		logger.debug("Uploading games...")
		try:
			games_upsert = supabase.table("game").upsert(games).execute()
			n_upserted = len(games_upsert.model_dump().get('data', []))
			logger.info(f"OK: upserted {n_upserted} games")
		except Exception as e:
			logger.error(f"Failed to upsert games: {e}")

	# Upsert Game Teams
	if game_teams:
		logger.debug("Uploading game teams...")
		try:
			game_teams_upsert = supabase.table("game_team").upsert(game_teams).execute()
			n_upserted = len(game_teams_upsert.model_dump().get('data', []))
			logger.info(f"OK: upserted {n_upserted} game teams")
		except Exception as e:
			logger.error(f"Failed to upsert game teams: {e}")

	logger.info("Finished schedule update")

def main():
	update_schedule_task()

if __name__ == "__main__":
	main()

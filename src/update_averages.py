from app.fetchers import get_player_averages
from app.parsers import parse_player_averages
from lib.utils import get_current_season

from lib.supabase import supabase
from lib.logger import logging

logger = logging.getLogger("backboard-logger")

def update_player_averages():
	logger.info("Starting daily update for player averages")

	# Fetch player averages
	season = get_current_season()
	logger.info(f"Fetching player averages for season {season}")
	player_averages_res = get_player_averages(season=season)
	
	if not player_averages_res:
		logger.error("Failed to fetch player averages")
		return

	player_averages = parse_player_averages(player_averages_res, season)

	logger.info(f"Found {len(player_averages)} player averages rows")

	# Upload data to supabase
	if player_averages:
		logger.info("Uploading player averages...")
		# Using the new table name: player_season_averages
		player_averages_upsert= supabase.table("player_season_averages").upsert(player_averages).execute()
		n_upserted = len(player_averages_upsert.model_dump()['data'])
		logger.info(f"OK: upserted {n_upserted} player averages rows")

def main():
	update_player_averages()

if __name__ == "__main__":
	main()
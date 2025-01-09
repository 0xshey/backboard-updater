from app.fetchers import get_player_averages
from app.parsers import parse_player_averages

from lib.supabase import supabase
from lib.logger import logging

logger = logging.getLogger("backboard-logger")

def update_player_averages():
	logger.info("Starting daily update for player averages")

	# Fetch player averages
	logger.info("Fetching player averages")
	player_averages_res = get_player_averages()
	
	if not player_averages_res:
		logger.error("Failed to fetch player averages")
		return

	player_averages = parse_player_averages(player_averages_res)

	logger.info(f"Found {len(player_averages)} player averages rows")

	# Upload data to supabase
	if player_averages:
		logger.info("Uploading player averages...")
		player_averages_upsert= supabase.table("PlayerSeasonAverages").upsert(player_averages).execute()
		n_upserted = len(player_averages_upsert.model_dump()['data'])
		logger.info(f"OK: upserted {n_upserted} player averages rows")

def main():
	update_player_averages()

if __name__ == "__main__":
	main()
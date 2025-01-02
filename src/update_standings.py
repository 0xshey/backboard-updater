from lib.logger import logging

from app.fetchers import get_standings
from app.parsers import parse_standings

logger = logging.getLogger("backboard-logger")

def daily_update_standings():
	logger.info("Starting daily update for standings")

	# Fetch standings
	logger.info("Fetching standings")
	standings_res = get_standings()
	
	if not standings_res:
		logger.error("Failed to fetch standings")
		return

	standings = parse_standings(standings_res)

	logger.info(f"Found {len(standings)} standings rows")

	# Upload data to supabase
	# ...

def main():
	daily_update_standings()

if __name__ == "__main__":
	main()
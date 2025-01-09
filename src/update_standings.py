from lib.logger import logging
from lib.supabase import supabase

from app.fetchers import get_standings
from app.parsers import parse_standings

logger = logging.getLogger("backboard-logger")

def update_standings():
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
	if standings:
		logger.info("Uploading standings...")
		standings_upsert= supabase.table("Standings").upsert(standings).execute()
		n_upserted = len(standings_upsert.model_dump()['data'])
		logger.info(f"OK: upserted {n_upserted} standings rows")
		

def main():
	update_standings()

if __name__ == "__main__":
	main()
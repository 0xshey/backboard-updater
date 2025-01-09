import time
import datetime
import argparse

from lib.logger import logging
from lib.supabase import supabase
from lib.utils import get_todays_date

from app.fetchers import get_game_ids, get_boxscore
from app.parsers import parse_boxscore

logger = logging.getLogger("backboard-logger")

def daily_update_games(date=get_todays_date()):
	logger.info(f"Starting daily update for date: {date}")

	if isinstance(date, str):
		dates = [date]

	for date in dates:
		# Fetch game_ids for the given date
		logger.info(f"Fetching games for: {date}")
		date_games = get_game_ids(date)

		for game_code, game_id in date_games.items():
			logger.debug(f"Fetching game: {game_code} (id: {game_id})")

			# Fetch boxscore for the game
			boxscore_res = get_boxscore(game_id)
			time.sleep(0.2)
			if not boxscore_res:
				continue

			game, game_teams, game_players = parse_boxscore(boxscore_res)

			# Display stats for the fetched data
			logger.debug(f"Found {len(game_players)} players")

			# Upload data to supabase
			if game:
				logger.debug("Uploading game...")
				game_upsert= supabase.table("Games").upsert([game]).execute()
				n_upserted = len(game_upsert.model_dump()['data'])
				logger.debug(f"OK: upserted {n_upserted} game rows")
			
			if game_teams:
				logger.debug("Uploading game_teams...")
				game_teams_upsert= supabase.table("GameTeams").upsert(game_teams).execute()
				n_upserted = len(game_teams_upsert.model_dump()['data'])
				logger.debug(f"OK: upserted {n_upserted} game_teams rows")

			if game_players:
				logger.debug("Uploading game_players...")
				game_players_upsert= supabase.table("GamePlayers").upsert(game_players).execute()
				n_upserted = len(game_players_upsert.model_dump()['data'])
				logger.debug(f"OK: upserted {n_upserted} game_players rows")

		logger.info(f"Finished updating games for date: {date}")
		
	logger.info("Finished update")


def daily_update_games_all():
	season_start = datetime.datetime.strptime("2024-10-22", "%Y-%m-%d")
	today = datetime.datetime.strptime(get_todays_date(), "%Y-%m-%d")

	dates = [(season_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range((today - season_start).days + 1)]

	for date in dates:
		daily_update_games(date)



def main():
	parser = argparse.ArgumentParser(description="Update games data")
	parser.add_argument("--date", type=str, help="Date for which to update games data (format: YYYY-MM-DD). Use 'all' to update all dates. If not provided, updates today's date.")
	args = parser.parse_args()

	if args.date == "all":
		daily_update_games_all()
	else:
		daily_update_games(date=args.date if args.date else get_todays_date())

if __name__ == "__main__":
	main()
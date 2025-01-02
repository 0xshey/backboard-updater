import time
from lib.logger import logging

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
		logger.info(f"Working on: {date}")
		date_games = get_game_ids(date)

		for game_code, game_id in date_games.items():
			logger.info(f"Fetching game: {game_code} (id: {game_id})")

			# Fetch boxscore for the game
			boxscore_res = get_boxscore(game_id)
			time.sleep(0.1)
			if not boxscore_res:
				continue

			game, game_teams, game_players = parse_boxscore(boxscore_res)

			# Display stats for the fetched data
			logger.info(f"Found {len(game_players)} players")

			# Upload data to supabase
			# ...

def main():
	daily_update_games()

if __name__ == "__main__":
	main()
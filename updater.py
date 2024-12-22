import logging
from supabase_client import supabase
from fetchers import fetch_games_and_standings, fetch_players_stats
import datetime
import argparse
import time

logger = logging.getLogger(__name__)
logging.basicConfig(
	filename='./logs/database.log',
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def do_job(update_type, date_str, all=False):
	logger.info("JOB STARTED")
	logger.info(f"Fetching data for date: {date_str}")

	try:
		if update_type == 'games':
			if all:
				print('--all is not yet implemented for games')

			# fetch games and standings
			games, standings = fetch_games_and_standings(date=date_str)

			# insert games
			if games:
				games_res = supabase.table("games").upsert(games).execute()
				n_upserted = len(games_res.model_dump()['data'])
				logger.info(f"Upserted {n_upserted} games for date: {date_str}")

			# insert standings
			if standings:
				standings_res = supabase.table("standings").upsert(standings).execute()
				n_upserted = len(standings_res.model_dump()['data'])
				logger.info(f"Upserted {n_upserted} standings for date: {date_str}")

		elif update_type == 'players':
			if all:
				games_to_fetch = supabase.table("games").select("id").execute().model_dump()['data']
			else:
				games_to_fetch = supabase.table("games").select("id").eq("date", date_str).execute().model_dump()['data']
			
			game_ids = [game['id'] for game in games_to_fetch]

			# fetch players
			logger.info(f"Fetching player data for {len(game_ids)} games")
			players = fetch_players_stats(game_ids)
			logger.info(f"Fetched {len(players)} players for date: {date_str}")

			# insert players
			if players:
				players_res = supabase.table("game_players").upsert(players).execute()
				n_upserted = len(players_res.model_dump()['data'])
				logger.info(f"Upserted {n_upserted} players for date: {date_str}")

		logger.info("Data update finished")

	except Exception as e:
		logger.error(f"ERROR: {e}")

	logger.info("JOB ENDED")	

def main():
	parser = argparse.ArgumentParser(description='Update Supabase with game or player data.')
	parser.add_argument('--type', choices=['games', 'players'], required=True, help='Type of data to update: games or players')
	parser.add_argument('--date', help='Date for which to fetch data in YYYY-MM-DD format. Defaults to today. Use "yesterday", "today", and "tomorrow" and they should function as expected.')
	parser.add_argument('--all', action='store_true', help='Update all data for all dates or games.')
	args = parser.parse_args()

	# determine the date based on the argument
	date_str = {
		'yesterday': (datetime.datetime.now() - datetime.timedelta(days=1)).date().isoformat(),
		'today': datetime.datetime.now().date().isoformat(),
		'tomorrow': (datetime.datetime.now() + datetime.timedelta(days=1)).date().isoformat()
	}.get(args.date.lower(), args.date) if args.date else datetime.datetime.now().date().isoformat()

	logger.info(f"Using date: {date_str}")

	start_time = time.time()
	do_job(update_type=args.type, date_str=date_str, all=args.all)
	end_time = time.time()
	print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
	main()

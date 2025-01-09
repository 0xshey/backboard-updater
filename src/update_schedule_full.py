import requests
import datetime
from lib.types import Game, GameTeam
from lib.supabase import supabase
from lib.logger import logging

logger = logging.getLogger("backboard-logger")

def update_schedule():
	logger.info("Starting update for schedule")
	schedule_url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"
	response = requests.get(schedule_url)
	data = response.json()
	game_dates = data['leagueSchedule']['gameDates']


	game_objs = []
	game_team_objs = []

	for game_date in game_dates:
		games = game_date['games']

		for i, game in enumerate(games):
			
			if game['gameLabel'] in ["Preseason", "All-Star Game"]:
				continue

			game_teams = {}
			for team_key in ['homeTeam', 'awayTeam']:
				game_team_data = {
					"gameId": str(game['gameId']),
					"teamId": str(game[team_key]['teamId']),
					"teamName": game[team_key]['teamName'],
					"teamCity": game[team_key]['teamCity'],
					"teamTricode": game[team_key]['teamTricode'],
					"score": game[team_key]['score'],
				}
				game_teams.update({team_key: game_team_data})
				game_team_objs.append(GameTeam(**game_team_data))
			

			game_objs.append(Game(
				gameId = str(game['gameId']),
				code = game['gameCode'],
				dateTimeUTC = game['gameDateTimeUTC'],
				dateTimeET = game['gameDateTimeEst'],
				order = i + 1,
				statusCode = game['gameStatus'],
				statusText = game['gameStatusText'],
				livePeriod = 1 if game['gameStatus'] == 1 else 3,
				arena = game['arenaName'],
				nationalBroadcaster = game["broadcasters"]["nationalBroadcasters"][0]["broadcasterDisplay"] if len(game["broadcasters"]["nationalBroadcasters"]) > 0 else "",
				homeTeamId = str(game['homeTeam']['teamId']),
				awayTeamId = str(game['awayTeam']['teamId']),
			))
		
	print(f"Found {len(game_objs)} games")
	print(f"Found {len(game_team_objs)} game teams")


	logger.info("Uploading games...")
	standings_upsert = supabase.table("Games").upsert(game_objs).execute()
	n_upserted = len(standings_upsert.model_dump()['data'])
	logger.info(f"OK: upserted {n_upserted} games")

	logger.info("Uploading game teams...")
	standings_upsert = supabase.table("GameTeams").upsert(game_team_objs).execute()
	n_upserted = len(standings_upsert.model_dump()['data'])
	logger.info(f"OK: upserted {n_upserted} game teams")


def main():
	update_schedule()

if __name__ == "__main__":
	main()

	

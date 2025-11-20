from json.decoder import JSONDecodeError
from lib.logger import logging
from lib.utils import get_todays_date

from nba_api.stats.endpoints import leaguestandingsv3, scoreboardv2
from nba_api.live.nba.endpoints import boxscore
from nba_api.stats.endpoints import leaguedashplayerstats

logger = logging.getLogger("backboard-logger")

def get_boxscore(game_id):
	""" for: Game, GamePlayer, GameTeam """
	try:
		logger.info(f"game: {game_id}")
		logger.debug(f"Making API request to nba_api...BoxScore for: {game_id}")
		response = boxscore.BoxScore(game_id=game_id).get_dict()
		logger.info("OK")
		return response

	except JSONDecodeError:
		logger.info("No data")
		return None
		
	except Exception as e:
		logger.error(f"BoxScore fetch FAILED: {e}")
		return None

def get_games(date=get_todays_date()):
	""" for: game_ids """
	logger.debug(f"Making API request to nba_api...ScoreboardV2 for: {date}")
	try:
		response = scoreboardv2.ScoreboardV2(game_date=date).get_normalized_dict()
		logger.info("OK")
		return response

	except Exception as e:
		logger.error(f"ScoreboardV2 fetch FAILED: {e}")
		return None

# game_id extractor
def get_game_ids(date=get_todays_date()):
	""" returns a list of game_ids for a given date """
	date_games = {}
	games = get_games(date)

	if games:
		for game in games['GameHeader']:
			date_games[game['GAMECODE']] = game['GAME_ID']
	else:
		logger.error("Failed to fetch game IDs")

	return date_games




# ----- LEGACY METHODS -----
# to be reimplemented eventually

def get_standings():
	""" for: Standing """
	logger.debug("Making API request to nba_api...LeagueStandingsV3")
	try:
		response = leaguestandingsv3.LeagueStandingsV3().get_normalized_dict()
		logger.info("OK")
		return response

	except Exception as e:
		logger.error(f"LeagueStandingsV3 fetch FAILED: {e}")
		return None

def get_player_averages():
	""" for: Player """
	logger.debug("Making API request to nba_api...LeagueDashPlayerStats")
	try:
		response = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed="PerGame").get_normalized_dict()
		logger.info("OK")
		return response

	except Exception as e:
		logger.error(f"LeagueDashPlayerStats fetch FAILED: {e}")
		return None


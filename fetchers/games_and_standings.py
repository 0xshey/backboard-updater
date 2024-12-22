from nba_api.stats.endpoints import scoreboardv2
import isodate
import utils

def fetch_games_and_standings(date: str):
	# Fetch data
	res = scoreboardv2.ScoreboardV2(game_date=date).get_normalized_dict()

	game_header_raw = res['GameHeader']
	line_score_raw = res['LineScore']
	east_standings_raw = res['EastConfStandingsByDay']
	west_standings_raw = res['WestConfStandingsByDay']

	games = _create_games(game_header_raw, line_score_raw)
	standings = _create_standings(east_standings_raw, west_standings_raw)

	return games, standings


def _create_standings(east_standings, west_standings):
	standings_colmap = {
		'STANDINGSDATE': {'rename': 'date'},
		'TEAM_ID': {'rename': 'teamId', 'lambda': lambda x: str(x)},
		'TEAM': {'rename': 'teamCity'},
		'CONFERENCE': {'rename': 'conference'},
		'G': {'rename': 'gamesPlayed'},
		'W': {'rename': 'wins'},
		'L': {'rename': 'losses'},
		'HOME_RECORD': {'rename': 'homeRecord'},
		'ROAD_RECORD': {'rename': 'awayRecord'},
	}

	standings = east_standings + west_standings
	standings = utils.apply_colmap_dict(standings, standings_colmap)

	return standings

def _create_games(game_header, line_score):
	# Parse game_header & line_score
	game_header_colmap = {
		'GAME_ID': { 'rename': 'id', },
		'GAMECODE': { 'rename': 'code', },
		'GAME_DATE_EST': {
			'rename': 'date',
			'lambda': lambda x: isodate.parse_datetime(x).date().isoformat(),
		},
		'GAME_SEQUENCE': { 'rename': 'order', },
		'GAME_STATUS_TEXT': { 
			'rename': 'statusText', 
			'lambda': lambda x: x.strip(),
		},
		'GAME_STATUS_ID': { 'rename': 'statusCode', },
		'HOME_TEAM_ID': { 
			'rename': 'homeTeam', 
			'lambda': lambda x: str(x), 
		},
		'VISITOR_TEAM_ID': { 
			'rename': 'awayTeam', 
			'lambda': lambda x: str(x), 
		},
		'LIVE_PERIOD': { 'rename': 'livePeriod', },
		'LIVE_PC_TIME': { 'rename': 'liveClock', },
		'ARENA_NAME': { 'rename': 'arena', },
		'NATL_TV_BROADCASTER_ABBREVIATION': { 'rename': 'nationalBroadcaster', },
	}

	games = utils.apply_colmap_dict(game_header, game_header_colmap)

	# Add extra data (linescore) to games
	extra_data = {}
	for row in line_score:
		new_row = {}
		period_scores = [row.get(f'PTS_QTR{i}') for i in range(1, 5)]
		period_scores += [row.get(f'PTS_OT{i}') for i in range(1, 11)]
		new_row['linescore'] = period_scores
		new_row['score'] = row.get('PTS')
		new_row['seasonRecord'] = row.get('TEAM_WINS_LOSSES')
		
		extra_data[str(row['TEAM_ID'])] = new_row

	# add extra data to game_header, based on teamId
	for game in games:
		game['homeTeamGame'] = extra_data[game['homeTeam']]
		game['awayTeamGame'] = extra_data[game['awayTeam']]

	return games

def fetch_players(date: str):
	# Fetch data
	pass
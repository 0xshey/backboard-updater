from nba_api.live.nba.endpoints import boxscore
from nba_api.stats.endpoints import leaguedashplayerstats
import utils
import time
import numpy as np

def fetch_players_stats(game_ids, date=None):
	all_players = []

	# Fetch season averages
	if not date:
		date = utils.get_todays_date()

	print(f"Fetching season averages for {date}")
	try:
		season_averages = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed="PerGame", date_to_nullable=date).get_normalized_dict()['LeagueDashPlayerStats']
		season_avgs_by_player = {}

		for player in season_averages:
			player_id = str(player['PLAYER_ID'])
			season_avgs_by_player[player_id] = {
				'pointsSeason': player['PTS'],
				'reboundsTotalSeason': player['REB'],
				'assistsSeason': player['AST'],
				'stealsSeason': player['STL'],
				'blocksSeason': player['BLK'],
				'turnoversSeason': player['TOV'],
				'fpSeason': player['NBA_FANTASY_PTS'],
				'minutesSeason': player['MIN']
			}

	except Exception as e:
		print('Error fetching season averages.', e)
		season_averages = None

	for game_id in game_ids:

		try:
			time.sleep(0.1)
			game = boxscore.BoxScore(game_id=game_id).get_dict()['game']


		except Exception as e:
			print('Error fetching players. The game probably has not begun yet.', e)
			continue

		print(f"Fetching game: {game_id}")
		# Fetch data
		game = boxscore.BoxScore(game_id=game_id).get_dict()['game']
		home_team_players_raw = game['homeTeam']['players']
		away_team_players_raw = game['awayTeam']['players']

		# Add team id to players
		for player in home_team_players_raw:
			player['teamId'] = str(game['homeTeam']['teamId'])
			player['opposingTeam'] = game['awayTeam']['teamId']
		
		for player in away_team_players_raw:
			player['teamId'] = str(game['awayTeam']['teamId'])
			player['opposingTeam'] = game['homeTeam']['teamId']

		# Combine players from both teams
		game_players = home_team_players_raw + away_team_players_raw

		still_playing = game['gameStatus'] == 2

		# unpack stats into top row and remove nested stats
		for row in game_players:
			row.update({stat: value for stat, value in row.pop('statistics').items()})

		players = []

		player_colmap = {
			'personId': {
				'rename': 'id',
				'lambda': str,
			},
			'familyName': { 'rename': 'lastName', },
			'jerseyNum': { 'rename': 'jersey', },
			'starter': { 
				'lambda': lambda x: bool(int(x)), 
			},
			'oncourt': {
				'rename': 'onCourt',
				'lambda': lambda x: bool(int(x)),
			},
			'played': {
				'lambda': lambda x: bool(int(x)),
			},
			'minutesCalculated': { 'drop': True },
			'name': { 'drop': True },
			'nameI': { 'drop': True },
		}

		players = utils.apply_colmap_dict(game_players, player_colmap, keep_other_columns=True)

		print('-> players: ', end='')
		for player in players:
			print('|', end='')
			player['stillPlaying'] = still_playing
			player['gameId'] = game_id

			# If player doesnt have these columns, add them
			for column in ['notPlayingReason', 'notPlayingDescription']:
				if column not in player:
					player[column] = ""

			player['fp'] = utils.calculate_fp(player)

			# ADD ADDITIONAL STATS
			minutes, seconds = utils.parse_iso_duration(player['minutes'])
			
			# FP and FP per minute
			if minutes == 0 and seconds == 0:
				player['fpPerMinute'] = 0
			else:
				exact_minutes = minutes + seconds / 60
				fp_per_minute = player['fp'] / exact_minutes
				player['fpPerMinute'] = round(fp_per_minute, 2)

			# Add season averages
			if season_avgs_by_player:
				player_averages = season_avgs_by_player.get(player['id'], None)

				if player_averages:
					player.update(player_averages)		
					player['fpDelta'] = round(player['fp'] - player['fpSeason'], 2)

				else:
					print(f"Player {player['id']} not found in season averages.")
					player.update(
						{
							'pointsSeason': None,
							'reboundsTotalSeason': None,
							'assistsSeason': None,
							'stealsSeason': None,
							'blocksSeason': None,
							'turnoversSeason': None,
							'fpSeason': None,
							'minutesSeason': None,
							'fpDelta': None,
						}
					)

			player['tags'] = []

			# has played tonight
			if player['played']: 
				player['tags'].append('played')
			
			# still playing
			if player['stillPlaying']: 
				player['tags'].append('still-playing')
			
			# good performers
			if (
				player['fp'] > 40 
				or (player['fpSeason'] and (player['fp'] >= (1.1 * player['fpSeason'] + (-0.012 * np.power(player['fpSeason'], 2) + 15))))
				or player['fpPerMinute'] > 1.2
			):
				player['tags'].append('good-list')
			
			# bad performers
			if (
				player['fpDelta'] and (player['fpDelta'] < -7 and not player['stillPlaying']) 
				or player['fpPerMinute'] < 0.6
			) and minutes > 10 and player['fp'] < 40:
				player['tags'].append('bad-list')\

			# brick-layer - fg% < 25%
			if player['fieldGoalsPercentage'] < 0.25 and player['fieldGoalsAttempted'] > 10:
				player['tags'].append('brick-layer')

			# efficient - fg% > 60%
			if player['fieldGoalsPercentage'] > 0.60 and player['fieldGoalsAttempted'] > 10:
				player['tags'].append('efficient')

			# sniper - 3pt% > 50%
			if player['threePointersPercentage'] > 0.50 and player['threePointersMade'] > 3:
				player['tags'].append('sniper')

			traditional_stats = ['points', 'reboundsTotal', 'assists', 'steals', 'blocks']
			
			# double-double
			if sum([player[stat] >= 10 for stat in traditional_stats]) >= 2:
				player['tags'].append('double-double')
			
			# triple-double
			if sum([player[stat] >= 10 for stat in traditional_stats]) >= 3:
				player['tags'].append('triple-double')

			# 5x5
			if sum([player[stat] >= 5 for stat in traditional_stats]) == 5:
				player['tags'].append('5x5')

			# butter-fingers - turnovers > 8
			if player['turnovers'] > 6:
				player['tags'].append('butter-fingers')

			# lockdown - stocks > 10
			if player['steals'] + player['blocks'] > 10:
				player['tags'].append('lockdown')

		print()

		players = sorted(players, key=lambda x: x['fp'], reverse=True)

		all_players += players

	return all_players
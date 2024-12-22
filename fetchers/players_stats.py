from nba_api.live.nba.endpoints import boxscore
import utils
import time

def fetch_players_stats(game_ids):
	all_players = []

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
			player['game'] = game_id

			# If player doesnt have these columns, add them
			for column in ['notPlayingReason', 'notPlayingDescription']:
				if column not in player:
					player[column] = ""

			player['fp'] = utils.calculate_fp(player)
		print()

		players = sorted(players, key=lambda x: x['fp'], reverse=True)

		all_players += players

	return all_players
from lib.types import Game, GameTeam, GamePlayer, SeasonAverage
from lib.utils import calculate_fp, parse_duration_to_seconds
from typing import List


def parse_boxscore(boxscore_response):
	if not boxscore_response:
		raise ValueError("Cannot parse boxscore response: None")

	boxscore_game = boxscore_response.get("game", {})
	boxscore_teams = [
		boxscore_game.get("homeTeam"),
		boxscore_game.get("awayTeam"),
	]

	game: Game
	game_teams: List[GameTeam] = []
	game_players: List[GamePlayer] = []

	# game
	game = Game(
		id=boxscore_game["gameId"],
		code=boxscore_game["gameCode"],
		# datetime_et=boxscore_game["gameTimeEst"],
		status_code=boxscore_game["gameStatus"],
		status_text=boxscore_game["gameStatusText"],
		datetime=boxscore_game["gameTimeUTC"],
		live_period=boxscore_game["period"],
		live_clock=boxscore_game["gameClock"],
		# label=boxscore_game["gameLabel"],
		# sublabel=boxscore_game["gameSubLabel"],
		arena_name=boxscore_game["arena"]["arenaName"],
		arena_state=boxscore_game["arena"]["arenaState"],
		arena_city=boxscore_game["arena"]["arenaCity"],
		# national_broadcaster=boxscore_game.get("nationalBroadcaster", ""),
		team_home_id=str(boxscore_game["homeTeam"]["teamId"]),
		team_away_id=str(boxscore_game["awayTeam"]["teamId"]),
		team_home_score=boxscore_game["homeTeam"]["score"],
		team_away_score=boxscore_game["awayTeam"]["score"]
	)

	# game teams
	for team in boxscore_teams:
		team_opp = next(t for t in boxscore_teams if t["teamId"] != team["teamId"])

		team_statistics = team.get("statistics")
		team_players = team.get("players", [])

		game_team = GameTeam(
			game_id=game["id"],
			team_id=str(team["teamId"]),
			team_opp_id=str(team_opp["teamId"]),
			# created_at

			seconds=parse_duration_to_seconds(team_statistics["minutes"]),
			time_leading=parse_duration_to_seconds(team_statistics["timeLeading"]),
			times_tied=int(team_statistics["timesTied"]),
			
			# Shooting splits
			field_goals_attempted=team_statistics["fieldGoalsAttempted"],
			field_goals_made=team_statistics["fieldGoalsMade"],
			field_goals_percentage=team_statistics["fieldGoalsPercentage"],
			three_pointers_attempted=team_statistics["threePointersAttempted"],
			three_pointers_made=team_statistics["threePointersMade"],
			three_pointers_percentage=team_statistics["threePointersPercentage"],
			free_throws_attempted=team_statistics["freeThrowsAttempted"],
			free_throws_made=team_statistics["freeThrowsMade"],
			free_throws_percentage=team_statistics["freeThrowsPercentage"],
			two_pointers_attempted=team_statistics["twoPointersAttempted"],
			two_pointers_made=team_statistics["twoPointersMade"],
			two_pointers_percentage=team_statistics["twoPointersPercentage"],

			true_shooting_attempts=team_statistics.get("trueShootingAttempts"),
			true_shooting_percentage=team_statistics.get("trueShootingPercentage"),

			# Rebounding
			rebounds_offensive=team_statistics["reboundsOffensive"],
			rebounds_defensive=team_statistics["reboundsDefensive"],
			rebounds_total=team_statistics["reboundsTotal"],
			rebounds_team=team_statistics["reboundsTeam"],
			rebounds_team_defensive=team_statistics["reboundsTeamDefensive"],
			rebounds_team_offensive=team_statistics["reboundsTeamOffensive"],

			# Fouls
			fouls_personal=team_statistics["foulsPersonal"],
			fouls_offensive=team_statistics["foulsOffensive"],
			fouls_drawn=team_statistics["foulsDrawn"],
			fouls_team=team_statistics["foulsTeam"],
			fouls_technical=team_statistics["foulsTechnical"],
			fouls_team_technical=team_statistics["foulsTeamTechnical"],

			# Offense
			points=team_statistics["points"],
			points_fast_break=team_statistics["pointsFastBreak"],
			points_fast_break_attempted=team_statistics.get("fastBreakPointsAttempted"),
			points_fast_break_made=team_statistics.get("fastBreakPointsMade"),
			points_fast_break_percentage=team_statistics.get("fastBreakPointsPercentage"),
			points_from_turnovers=team_statistics["pointsFromTurnovers"],
			points_in_the_paint=team_statistics["pointsInThePaint"],
			points_in_the_paint_attempted=team_statistics.get("pointsInThePaintAttempted"),
			points_in_the_paint_made=team_statistics.get("pointsInThePaintMade"),
			points_in_the_paint_percentage=team_statistics.get("pointsInThePaintPercentage"),
			points_second_chance=team_statistics["pointsSecondChance"],
			points_second_chance_attempted=team_statistics.get("secondChancePointsAttempted"),
			points_second_chance_made=team_statistics.get("secondChancePointsMade"),
			points_second_chance_percentage=team_statistics.get("secondChancePointsPercentage"),
			team_field_goals_attempted=team_statistics["teamFieldGoalAttempts"],
			bench_points=team_statistics["benchPoints"],
			biggest_lead=team_statistics.get("biggestLead", 0),
			biggest_scoring_run=team_statistics.get("biggestScoringRun", 0),
			assists=team_statistics["assists"],

			# Defense
			steals=team_statistics["steals"],
			blocks=team_statistics["blocks"],
			points_against=team_statistics["pointsAgainst"],
			turnovers=team_statistics["turnovers"],
			turnovers_team=team_statistics["turnoversTeam"],
			turnovers_total=team_statistics.get("turnoversTotal"),
			assist_turnover_ratio=team_statistics.get("assistTurnoverRatio"),

			# Other
			plus_minus=team_statistics["points"] - team_statistics["pointsAgainst"],
			
		)
		game_teams.append(game_team)

		# players
		for player in team_players:
			player_statistics = player.get("statistics")

			game_player = GamePlayer(
				game_id=str(game["id"]),
				player_id=str(player["personId"]),
				team_id=str(team["teamId"]),
				team_opp_id=str(team_opp["teamId"]),

				# Schema: status
				status=player["status"],

				# Schema: starter, played, still_playing
				starter=bool(int(player["starter"])),
				played=bool(int(player["played"])),
				still_playing=player.get("stillPlaying"),  # unsure: comment if not provided
				on_court=bool(int(player["oncourt"])),

				# Schema: not_playing_reason, not_playing_description
				not_playing_reason=player.get("notPlayingReason"),
				not_playing_description=player.get("notPlayingDescription"),

				# Schema: first_name, last_name
				first_name=player["firstName"],
				last_name=player["familyName"],

				# Schema: jersey_number
				jersey_number=player.get("jerseyNum"),

				# Schema: starting_position
				starting_position=player.get("position", ""),

				# Schema: assists, blocks, blocks_received
				assists=player_statistics["assists"],
				blocks=player_statistics["blocks"],
				blocks_received=player_statistics.get("blocksReceived"),

				# Schema: field_goals_*
				field_goals_attempted=player_statistics["fieldGoalsAttempted"],
				field_goals_made=player_statistics["fieldGoalsMade"],
				field_goals_percentage=player_statistics["fieldGoalsPercentage"],

				# Schema: fouls_*
				fouls_offensive=player_statistics.get("foulsOffensive"),
				fouls_drawn=player_statistics.get("foulsDrawn"),
				fouls_personal=player_statistics["foulsPersonal"],
				fouls_technical=player_statistics.get("foulsTechnical"),

				# Schema: free_throws_*
				free_throws_attempted=player_statistics["freeThrowsAttempted"],
				free_throws_made=player_statistics["freeThrowsMade"],
				free_throws_percentage=player_statistics["freeThrowsPercentage"],

				# Schema: minus, plus, plus_minus
				minus=int(player_statistics["minus"]),
				plus=int(player_statistics["plus"]),
				plus_minus=int(player_statistics.get("plusMinusPoints")),

				# Schema: seconds (your source uses "minutes" – converted)
				seconds=parse_duration_to_seconds(player_statistics["minutes"]),

				# Schema: points
				points=player_statistics["points"],
				points_fast_break=player_statistics.get("pointsFastBreak"),
				points_in_the_paint=player_statistics["pointsInThePaint"],
				points_second_chance=player_statistics["pointsSecondChance"],

				# Schema: rebounds_*
				rebounds_defensive=player_statistics["reboundsDefensive"],
				rebounds_offensive=player_statistics["reboundsOffensive"],
				rebounds_total=player_statistics["reboundsTotal"],

				# Schema: steals
				steals=player_statistics["steals"],

				# Schema: three_pointers_*
				three_pointers_attempted=player_statistics["threePointersAttempted"],
				three_pointers_made=player_statistics["threePointersMade"],
				three_pointers_percentage=player_statistics["threePointersPercentage"],

				# Schema: turnovers
				turnovers=player_statistics["turnovers"],

				# Schema: two_pointers_*
				two_pointers_attempted=player_statistics["twoPointersAttempted"],
				two_pointers_made=player_statistics["twoPointersMade"],
				two_pointers_percentage=player_statistics["twoPointersPercentage"],

				# Schema: fp
				fp=calculate_fp(player_statistics),

				# Fields in your original mapping but NOT in schema:
				# order=player["order"],                     # not in schema
				# jersey_num=player["jerseyNum"],            # replaced with jersey_number
				# fantasy_points=calculate_fp(player_stats), # replaced with fp
			)

			game_players.append(game_player)

	return game, game_teams, game_players



# ----- LEGACY METHODS -----

def parse_player_averages(player_averages_response, season):
	""" for: SeasonAverage """
	if not player_averages_response:
		raise ValueError("Cannot parse player averages response: None")
	
	data = player_averages_response.get("LeagueDashPlayerStats", [])

	averages: List[SeasonAverage] = []
	for row in data:
		averages.append(SeasonAverage(
			season=season,
			player_id=str(row['PLAYER_ID']),
			team_id=str(row['TEAM_ID']),
			age=int(row['AGE']),
			games_played=int(row['GP']),
			wins=int(row['W']),
			losses=int(row['L']),
			win_percentage=float(row['W_PCT']),
			minutes_average=float(row['MIN']),
			field_goals_made=float(row['FGM']),
			field_goals_attempted=float(row['FGA']),
			field_goals_percentage=float(row['FG_PCT']),
			three_pointers_made=float(row['FG3M']),
			three_pointers_attempted=float(row['FG3A']),
			three_pointers_percentage=float(row['FG3_PCT']),
			free_throws_made=float(row['FTM']),
			free_throws_attempted=float(row['FTA']),
			free_throws_percentage=float(row['FT_PCT']),
			rebounds_offensive=float(row['OREB']),
			rebounds_defensive=float(row['DREB']),
			rebounds_total=float(row['REB']),
			assists=float(row['AST']),
			turnovers=float(row['TOV']),
			steals=float(row['STL']),
			blocks=float(row['BLK']),
			blocks_received=float(row['BLKA']),
			fouls_personal=float(row['PF']),
			fouls_drawn=float(row['PFD']),
			points=float(row['PTS']),
			plus_minus=float(row['PLUS_MINUS']),
			nba_fantasy_points=float(row['NBA_FANTASY_PTS']),
			double_doubles=int(row['DD2']),
			triple_doubles=int(row['TD3']),

			wins_rank=int(row['W_RANK']),
			losses_rank=int(row['L_RANK']),
			win_percentage_rank=int(row['W_PCT_RANK']),
			minutes_average_rank=int(row['MIN_RANK']),
			field_goals_made_rank=int(row['FGM_RANK']),
			field_goals_attempted_rank=int(row['FGA_RANK']),
			field_goals_percentage_rank=int(row['FG_PCT_RANK']),
			three_pointers_made_rank=int(row['FG3M_RANK']),
			three_pointers_attempted_rank=int(row['FG3A_RANK']),
			three_pointers_percentage_rank=int(row['FG3_PCT_RANK']),
			free_throws_made_rank=int(row['FTM_RANK']),
			free_throws_attempted_rank=int(row['FTA_RANK']),
			free_throws_percentage_rank=int(row['FT_PCT_RANK']),
			rebounds_offensive_rank=int(row['OREB_RANK']),
			rebounds_defensive_rank=int(row['DREB_RANK']),
			rebounds_total_rank=int(row['REB_RANK']),
			assists_rank=int(row['AST_RANK']),
			turnovers_rank=int(row['TOV_RANK']),
			steals_rank=int(row['STL_RANK']),
			blocks_rank=int(row['BLK_RANK']),
			blocks_received_rank=int(row['BLKA_RANK']),
			fouls_personal_rank=int(row['PF_RANK']),
			fouls_drawn_rank=int(row['PFD_RANK']),
			points_rank=int(row['PTS_RANK']),
			plus_minus_rank=int(row['PLUS_MINUS_RANK']),
			nba_fantasy_points_rank=int(row['NBA_FANTASY_PTS_RANK']),
			double_doubles_rank=int(row['DD2_RANK']),
			triple_doubles_rank=int(row['TD3_RANK']),
		))
	
	return averages
	
def parse_schedule(schedule_response):
	""" for: Game, GameTeam """
	if not schedule_response:
		raise ValueError("Cannot parse schedule response: None")

	league_schedule = schedule_response.get('leagueSchedule', {})
	game_dates = league_schedule.get('gameDates', [])

	games_data: List[Game] = []
	games_teams_data: List[GameTeam] = []

	for game_date in game_dates:
		for i, game in enumerate(game_date['games']):
			
			# Skip non-regular season games if needed, or handle them.
			# The prompt didn't strictly say to filter, but the previous code did:
			if game['gameLabel'] in ["Preseason", "All-Star Game"]:
				continue

			# Game object
			# Mapping based on previous update_schedule_full.py and types.py
			# Note: types.py has fields like 'week_nba', 'label', etc. 
			# I will map what is available.
			
			game_obj = Game(
				id=str(game['gameId']),
				# created_at is strictly required by TypedDict but usually handled by DB default or current time? 
				# In parsers.py generally we don't set created_at if it's not from source, 
				# but TypedDict might complain if I try to instantiate it strictly.
				# However, looking at parse_boxscore, it sets fields. 
				# Wait, parse_boxscore sets:
				# game = Game(id=..., ...)
				# It does NOT set created_at. So it must be Optional in runtime or Supabase ignores it?
				# Let's look at types.py again. Game(TypedDict) has created_at: str.
				# But TypedDict doesn't enforce keys at runtime unless validated.
				# I will follow parse_boxscore pattern and omit created_at if not derived.
				
				code=game['gameCode'],
				datetime=game['gameDateTimeUTC'], # mapping to 'datetime'
				# datetime_et=game['gameDateTimeEst'], # Not in Game TypedDict currently shown? 
				# Let's check Game TypedDict in types.py... 
				# Game has: id, created_at, status_code, status_text, datetime, week_nba, label, sublabel, arena_name, arena_state, arena_city, team_home_id, team_away_id, team_home_score, team_away_score.
				
				status_code=game['gameStatus'],
				status_text=game['gameStatusText'],
				week_nba=game['weekNumber'], # assuming this exists
				label=game['gameLabel'],
				sublabel=game['gameSubLabel'],
				arena_name=game['arenaName'],
				arena_state=game['arenaState'],
				arena_city=game['arenaCity'],
				team_home_id=str(game['homeTeam']['teamId']),
				team_away_id=str(game['awayTeam']['teamId']),
				team_home_score=game['homeTeam']['score'],
				team_away_score=game['awayTeam']['score']
			)
			games_data.append(game_obj)

			# GameTeam objects
			for team_key in ['homeTeam', 'awayTeam']:
				team_data = game[team_key]
				# We need team_opp_id
				opp_key = 'awayTeam' if team_key == 'homeTeam' else 'homeTeam'
				opp_data = game[opp_key]

				game_team_obj = GameTeam(
					game_id=str(game['gameId']),
					team_id=str(team_data['teamId']),
					team_opp_id=str(opp_data['teamId']),
					# Schema match...
					# Update_schedule_full had: teamName, teamCity, teamTricode -> These are Team fields, not GameTeam fields in types.py?
					# GameTeam in types.py has stats (field_goals_made, etc.)
					# The schedule endpoint mainly gives scores.
					# GameTeam has 'points' which can be 'score'.
					points=team_data['score']
				)
				# Only append if we have meaningful data? 
				# The schedule endpoint is sparse on stats. 
				# But for future games, it might just be the matchup.
				games_teams_data.append(game_team_obj)

	# Deduplicate game_teams based on game_id and team_id
	unique_game_teams = { (gt['game_id'], gt['team_id']): gt for gt in games_teams_data }
	games_teams_data = list(unique_game_teams.values())
	
	# Also deduplicate games just in case
	unique_games = { g['id']: g for g in games_data }
	games_data = list(unique_games.values())

	return games_data, games_teams_data


def parse_standings(standings_response):
	""" for: Standing """
	if not standings_response:
		raise ValueError("Cannot parse staning response: None")
	
	# standings: List[Standing] = []
	standings = []
	for row in standings_response.get("Standings", []):
		standing = Standing(
			teamId=str(row["TeamID"]),
			seasonId=row["SeasonID"],
			teamCity=row["TeamCity"],
			conference=row["Conference"],
			division=row["Division"],
			gamesPlayed=row["WINS"] + row["LOSSES"],
			wins=row["WINS"],
			losses=row["LOSSES"],
			winPct=row["WinPCT"],
			clinchedConference=bool(row["ClinchedConferenceTitle"]),
			clinchedDivision=bool(row["ClinchedDivisionTitle"]),
			clinchedPlayoff=bool(row["ClinchedPlayoffBirth"]),
			clinchedPlayIn=bool(row["ClinchedPlayIn"]),
			eliminatedConference=bool(row["EliminatedConference"]),
			eliminatedDivision=bool(row["EliminatedDivision"]),
			conferenceRank=row["PlayoffRank"],
			divisionRank=row["DivisionRank"],
			conferenceRecord=row["ConferenceRecord"].strip(),
			divisionRecord=row["DivisionRecord"].strip(),
			homeRecord=row["HOME"].strip(),
			awayRecord=row["ROAD"].strip(),
			l10Record=row["L10"].strip(),
			homeStreak=row["CurrentHomeStreak"],
			awayStreak=row["CurrentRoadStreak"],
			pointsFor=row["TotalPoints"],
			pointsAgainst=row["OppTotalPoints"],
		)
		standings.append(standing)
	return standings


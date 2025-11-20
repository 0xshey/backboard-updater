from lib.types import Game, GameTeam, GamePlayer
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
		# live_period=boxscore_game["period"],
		# live_clock=boxscore_game["gameClock"],
		# label=boxscore_game["gameLabel"],
		# sublabel=boxscore_game["gameSubLabel"],
		arena_name=boxscore_game["arena"]["arenaName"],
		arena_state=boxscore_game["arena"]["arenaState"],
		arena_city=boxscore_game["arena"]["arenaCity"],
		# national_broadcaster=boxscore_game.get("nationalBroadcaster", ""),
		team_home_id=str(boxscore_game["homeTeam"]["teamId"]),
		team_away_id=str(boxscore_game["awayTeam"]["teamId"]),
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

def parse_player_averages(player_averages_response):
	""" for: Player """
	if not player_averages_response:
		raise ValueError("Cannot parse player averages response: None")
	
	data = player_averages_response.get("LeagueDashPlayerStats", [])

	# players: List[PlayerSeasonAverages] = []
	players = []
	for row in data:
		players.append(PlayerSeasonAverages(
			playerId=str(row['PLAYER_ID']),
			playerName=row['PLAYER_NAME'],
			playerAge=int(row['AGE']),
			teamId=str(row['TEAM_ID']),
			teamTricode=row['TEAM_ABBREVIATION'],
			gamesPlayed=int(row['GP']),
			wins=int(row['W']),
			losses=int(row['L']),
			winPercentage=float(row['W_PCT']),
			minutes=float(row['MIN']),
			fieldGoalsMade=float(row['FGM']),
			fieldGoalsAttempted=float(row['FGA']),
			fieldGoalsPercentage=float(row['FG_PCT']),
			threePointersMade=float(row['FG3M']),
			threePointersAttempted=float(row['FG3A']),
			threePointersPercentage=float(row['FG3_PCT']),
			freeThrowsMade=float(row['FTM']),
			freeThrowsAttempted=float(row['FTA']),
			freeThrowsPercentage=float(row['FT_PCT']),
			reboundsOffensive=float(row['OREB']),
			reboundsDefensive=float(row['DREB']),
			reboundsTotal=float(row['REB']),
			assists=float(row['AST']),
			turnovers=float(row['TOV']),
			steals=float(row['STL']),
			blocks=float(row['BLK']),
			blocksReceived=float(row['BLKA']),
			foulsPersonal=float(row['PF']),
			foulsDrawn=float(row['PFD']),
			points=float(row['PTS']),
			plusMinusPoints=float(row['PLUS_MINUS']),
			fantasyPoints=float(row['NBA_FANTASY_PTS']),
			doubleDoubles=float(row['DD2']),
			tripleDoubles=float(row['TD3']),
			gamesPlayedRank=int(row['GP_RANK']),
			winsRank=int(row['W_RANK']),
			lossesRank=int(row['L_RANK']),
			winPercentageRank=int(row['W_PCT_RANK']),
			minutesRank=int(row['MIN_RANK']),
			fieldGoalsMadeRank=int(row['FGM_RANK']),
			fieldGoalsAttemptedRank=int(row['FGA_RANK']),
			fieldGoalsPercentageRank=int(row['FG_PCT_RANK']),
			threePointersMadeRank=int(row['FG3M_RANK']),
			threePointersAttemptedRank=int(row['FG3A_RANK']),
			threePointersPercentageRank=int(row['FG3_PCT_RANK']),
			freeThrowsMadeRank=int(row['FTM_RANK']),
			freeThrowsAttemptedRank=int(row['FTA_RANK']),
			freeThrowsPercentageRank=int(row['FT_PCT_RANK']),
			reboundsOffensiveRank=int(row['OREB_RANK']),
			reboundsDefensiveRank=int(row['DREB_RANK']),
			reboundsTotalRank=int(row['REB_RANK']),
			assistsRank=int(row['AST_RANK']),
			turnoversRank=int(row['TOV_RANK']),
			stealsRank=int(row['STL_RANK']),
			blocksRank=int(row['BLK_RANK']),
			blocksReceivedRank=int(row['BLKA_RANK']),
			foulsPersonalRank=int(row['PF_RANK']),
			foulsDrawnRank=int(row['PFD_RANK']),
			pointsRank=int(row['PTS_RANK']),
			plusMinusPointsRank=int(row['PLUS_MINUS_RANK']),
			fantasyPointsRank=int(row['NBA_FANTASY_PTS_RANK']),
			doubleDoublesRank=int(row['DD2_RANK']),
			tripleDoublesRank=int(row['TD3_RANK']),
		))
	
	return players

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


from lib.types import Standing, Game, GameTeam, GamePlayer
from typing import List

def parse_standings(standings_response):
	""" for: Standing """
	if not standings_response:
		raise ValueError("Cannot parse staning response: None")
	
	standings: List[Standing] = []
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

def parse_boxscore(boxscore_response):
	if not boxscore_response:
		raise ValueError("Cannot parse boxscore response: None")

	boxscore_game = boxscore_response.get('game', {})
	boxscore_teams = [
		boxscore_game.get('homeTeam'),
		boxscore_game.get('awayTeam'),
	]

	game: Game
	game_teams: List[GameTeam] = []
	game_players: List[GamePlayer] = []

	# game
	game = Game(
		gameId=boxscore_game['gameId'],
		code=boxscore_game['gameCode'],
		dateTimeUTC=boxscore_game['gameTimeUTC'],
		order=boxscore_game['gameStatus'],
		statusCode=boxscore_game['gameStatus'],
		statusText=boxscore_game['gameStatusText'],
		livePeriod=boxscore_game['period'],
		liveClock=boxscore_game['gameClock'],
		arena=boxscore_game['arena']['arenaName'],
		nationalBroadcaster=boxscore_game.get('nationalBroadcaster', ''),
		homeTeamId=str(boxscore_game['homeTeam']['teamId']),
		awayTeamId=str(boxscore_game['awayTeam']['teamId']),
	)

	# game teams
	for team in boxscore_teams:
		team_statistics = team.get('statistics')
		team_players = team.get('players', [])
		game_team = GameTeam(
			gameId=game['gameId'],
			teamId=str(team['teamId']),
			teamName=team['teamName'],
			teamCity=team['teamCity'],
			teamTricode=team['teamTricode'],
			score=team['score'],
			inBonus=team['inBonus'],
			timeoutsRemaining=team['timeoutsRemaining'],
			periods=team['periods'],
			points=team_statistics['points'],
			assists=team_statistics['assists'],
			reboundsTotal=team_statistics['reboundsTotal'],
			steals=team_statistics['steals'],
			turnovers=team_statistics['turnovers'],
			blocks=team_statistics['blocks'],
			assistsTurnoverRatio=team_statistics['assistsTurnoverRatio'],
			benchPoints=team_statistics['benchPoints'],
			biggestLead=team_statistics.get('biggestLead', 0),
			biggestLeadScore=team_statistics.get('biggestLeadScore', ''),
			biggestScoringRun=team_statistics.get('biggestScoringRun', 0),
			biggestScoringRunScore=team_statistics.get('biggestScoringRunScore', ''),
			blocksReceived=team_statistics['blocksReceived'],
			fastBreakPointsAttempted=team_statistics['fastBreakPointsAttempted'],
			fastBreakPointsMade=team_statistics['fastBreakPointsMade'],
			fastBreakPointsPercentage=team_statistics['fastBreakPointsPercentage'],
			fieldGoalsAttempted=team_statistics['fieldGoalsAttempted'],
			fieldGoalsEffectiveAdjusted=team_statistics['fieldGoalsEffectiveAdjusted'],
			fieldGoalsMade=team_statistics['fieldGoalsMade'],
			fieldGoalsPercentage=team_statistics['fieldGoalsPercentage'],
			foulsOffensive=team_statistics['foulsOffensive'],
			foulsDrawn=team_statistics['foulsDrawn'],
			foulsPersonal=team_statistics['foulsPersonal'],
			foulsTeam=team_statistics['foulsTeam'],
			foulsTechnical=team_statistics['foulsTechnical'],
			foulsTeamTechnical=team_statistics['foulsTeamTechnical'],
			freeThrowsAttempted=team_statistics['freeThrowsAttempted'],
			freeThrowsMade=team_statistics['freeThrowsMade'],
			freeThrowsPercentage=team_statistics['freeThrowsPercentage'],
			leadChanges=team_statistics['leadChanges'],
			minutes=team_statistics['minutes'],
			pointsAgainst=team_statistics['pointsAgainst'],
			pointsFastBreak=team_statistics['pointsFastBreak'],
			pointsFromTurnovers=team_statistics['pointsFromTurnovers'],
			pointsInThePaint=team_statistics['pointsInThePaint'],
			pointsInThePaintAttempted=team_statistics['pointsInThePaintAttempted'],
			pointsInThePaintMade=team_statistics['pointsInThePaintMade'],
			pointsInThePaintPercentage=team_statistics['pointsInThePaintPercentage'],
			pointsSecondChance=team_statistics['pointsSecondChance'],
			reboundsDefensive=team_statistics['reboundsDefensive'],
			reboundsOffensive=team_statistics['reboundsOffensive'],
			reboundsPersonal=team_statistics['reboundsPersonal'],
			reboundsTeam=team_statistics['reboundsTeam'],
			reboundsTeamDefensive=team_statistics['reboundsTeamDefensive'],
			reboundsTeamOffensive=team_statistics['reboundsTeamOffensive'],
			secondChancePointsAttempted=team_statistics['secondChancePointsAttempted'],
			secondChancePointsMade=team_statistics['secondChancePointsMade'],
			secondChancePointsPercentage=team_statistics['secondChancePointsPercentage'],
			teamFieldGoalAttempts=team_statistics['teamFieldGoalAttempts'],
			threePointersAttempted=team_statistics['threePointersAttempted'],
			threePointersMade=team_statistics['threePointersMade'],
			threePointersPercentage=team_statistics['threePointersPercentage'],
			timeLeading=team_statistics['timeLeading'],
			timesTied=team_statistics['timesTied'],
			trueShootingAttempts=team_statistics['trueShootingAttempts'],
			trueShootingPercentage=team_statistics['trueShootingPercentage'],
			turnoversTeam=team_statistics['turnoversTeam'],
			turnoversTotal=team_statistics['turnoversTotal'],
			twoPointersAttempted=team_statistics['twoPointersAttempted'],
			twoPointersMade=team_statistics['twoPointersMade'],
			twoPointersPercentage=team_statistics['twoPointersPercentage'],
		)
		game_teams.append(game_team)

		# players
		for player in team_players:
			player_statistics = player.get('statistics')
			game_player = GamePlayer(
				gameId=str(game["gameId"]),
				playerId=str(player["personId"]),
				teamId=str(team["teamId"]),
				status=player["status"],
				order=player["order"],
				jerseyNum=player["jerseyNum"],
				startingPosition=player.get("position", ""),
				starter=bool(int(player["starter"])),
				oncourt=bool(int(player["oncourt"])),
				played=bool(int(player["played"])),
				assists=player_statistics["assists"],
				blocks=player_statistics["blocks"],
				blocksReceived=player_statistics["blocksReceived"],
				fieldGoalsAttempted=player_statistics["fieldGoalsAttempted"],
				fieldGoalsMade=player_statistics["fieldGoalsMade"],
				fieldGoalsPercentage=player_statistics["fieldGoalsPercentage"],
				foulsOffensive=player_statistics["foulsOffensive"],
				foulsDrawn=player_statistics["foulsDrawn"],
				foulsPersonal=player_statistics["foulsPersonal"],
				foulsTechnical=player_statistics["foulsTechnical"],
				freeThrowsAttempted=player_statistics["freeThrowsAttempted"],
				freeThrowsMade=player_statistics["freeThrowsMade"],
				freeThrowsPercentage=player_statistics["freeThrowsPercentage"],
				minus=player_statistics["minus"],
				minutes=player_statistics["minutes"],
				plus=player_statistics["plus"],
				plusMinusPoints=player_statistics["plusMinusPoints"],
				points=player_statistics["points"],
				pointsFastBreak=player_statistics["pointsFastBreak"],
				pointsInThePaint=player_statistics["pointsInThePaint"],
				pointsSecondChance=player_statistics["pointsSecondChance"],
				reboundsDefensive=player_statistics["reboundsDefensive"],
				reboundsOffensive=player_statistics["reboundsOffensive"],
				reboundsTotal=player_statistics["reboundsTotal"],
				steals=player_statistics["steals"],
				threePointersAttempted=player_statistics["threePointersAttempted"],
				threePointersMade=player_statistics["threePointersMade"],
				threePointersPercentage=player_statistics["threePointersPercentage"],
				turnovers=player_statistics["turnovers"],
				twoPointersAttempted=player_statistics["twoPointersAttempted"],
				twoPointersMade=player_statistics["twoPointersMade"],
				twoPointersPercentage=player_statistics["twoPointersPercentage"],
				firstName=player["firstName"],
				lastName=player["familyName"]
			)
			game_players.append(game_player)

	return game, game_teams, game_players
	
#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect(database="tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM match")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM player")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT COUNT (*) FROM player")
    count = c.fetchall()
    DB.commit()
    DB.close()
    return int(count[0][0])


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """

    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO player (player_name) VALUES (%s)", (name,))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    query = """
                    SELECT player_wins.id , player_wins.name, player_wins.wins, player_wins.wins + player_loses.loses
                    as matches FROM

                    (SELECT player.player_id AS id ,player.player_name AS name, Count(match.winner_id) AS wins
                     FROM
                    player LEFT JOIN match
                    ON player.player_id = match.winner_id GROUP BY (player.player_id)
                    order by wins DESC ) AS player_wins

                    LEFT JOIN

                    (SELECT player.player_id AS id , player.player_name AS name, Count(match.loser_id) AS loses
                    FROM player LEFT JOIN match
                    ON player.player_id = match.loser_id GROUP BY (player.player_id)
                    order by loses DESC) AS player_loses on player_wins.id = player_loses.id ;


            """

    DB = connect()
    c = DB.cursor()
    c.execute(query)
    result = c.fetchall()
    DB.commit()
    DB.close()
    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO match (winner_id,loser_id) VALUES (%s,%s)", ((winner,), (loser,)))
    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    result = playerStandings()
    finalResult = []

    for j in range(0, len(result)):
        if j % 2 == 0:
            finalResult.append((result[j][0], result[j][1], result[j + 1][0], result[j + 1][1]))

    return finalResult

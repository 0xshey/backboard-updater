import pandas as pd
import datetime
import pytz
from lib.supabase import supabase
from lib.logger import logging

logger = logging.getLogger("backboard-logger")

def get_ny_date():
    """Returns the current date in New York timezone."""
    ny_tz = pytz.timezone('America/New_York')
    now = datetime.datetime.now(ny_tz)
    return now.strftime('%Y-%m-%d')

def update_consistency():
    logger.info("Starting daily update for consistency metrics")
    
    ny_date = get_ny_date()
    logger.info(f"As of Date (NY): {ny_date}")

    # 1. Fetch top 200 players by fantasy points from player_season_averages
    logger.info("Fetching top 200 players from player_season_averages...")
    response = supabase.table('player_season_averages') \
        .select('player_id') \
        .order('nba_fantasy_points', desc=True) \
        .limit(200) \
        .execute()
    
    if not response.data:
        logger.error("No player averages found.")
        return

    top_player_ids = [p['player_id'] for p in response.data]
    logger.info(f"Identified {len(top_player_ids)} top players.")

    # 2. Fetch game logs for these players
    # We fetch relevant columns: player_id, fp (fantasy points), played, and player details
    logger.info("Fetching game logs for top players...")
    all_games = []
    
    batch_size = 50
    for i in range(0, len(top_player_ids), batch_size):
        batch_ids = top_player_ids[i:i + batch_size]
        
        # Join with game table to get datetime for sorting
        resp = supabase.table('game_player') \
            .select('player_id, fp, played, game_id, game(datetime), player(first_name, last_name)') \
            .in_('player_id', batch_ids) \
            .execute()
            
        if resp.data:
            all_games.extend(resp.data)
            
    logger.info(f"Fetched {len(all_games)} game logs.")
    
    if not all_games:
        logger.error("No game logs found for top players.")
        return

    # 3. Process Data
    df_games = pd.DataFrame(all_games)
    
    # Flatten details
    df_games['first_name'] = df_games['player'].apply(lambda x: x.get('first_name') if x else None)
    df_games['last_name'] = df_games['player'].apply(lambda x: x.get('last_name') if x else None)
    df_games['datetime'] = df_games['game'].apply(lambda x: x.get('datetime') if x else None)
    
    # Convert 'datetime' to datetime for L10 sorting
    df_games['datetime'] = pd.to_datetime(df_games['datetime'])

    # Determine metrics
    stats_col = 'fp'
    
    results = []
    
    grouped = df_games.groupby('player_id')
    
    for player_id, group in grouped:
        # Player info (take from first row)
        first_name = group['first_name'].iloc[0]
        last_name = group['last_name'].iloc[0]
        
        # --- Overall Season Metrics ---
        # "games_missed" based on played=False
        games_missed_count = group[group['played'] == False].shape[0]
        
        # Played games for stats
        played_games = group[group['played'] == True]
        games_played_count = played_games.shape[0]
        
        if games_played_count > 0:
            avg_fp = played_games[stats_col].mean()
            std_fp = played_games[stats_col].std()
            # If standard deviation is NaN (1 game), fill with 0
            if pd.isna(std_fp):
                std_fp = 0.0
            variation_pct = (std_fp / avg_fp) * 100 if avg_fp > 0 else 0.0
        else:
            avg_fp = 0.0
            std_fp = 0.0
            variation_pct = 0.0
            
        # --- L10 Metrics ---
        # Sort by datetime desc to get last 10
        last_10_played = played_games.sort_values('datetime', ascending=False).head(10)
        
        if not last_10_played.empty:
            l10_avg_fp = last_10_played[stats_col].mean()
            l10_std_fp = last_10_played[stats_col].std()
            if pd.isna(l10_std_fp):
                l10_std_fp = 0.0
            l10_variation_pct = (l10_std_fp / l10_avg_fp) * 100 if l10_avg_fp > 0 else 0.0
        else:
            l10_avg_fp = 0.0
            l10_std_fp = 0.0
            l10_variation_pct = 0.0
            
        record = {
            'as_of_date': ny_date,
            'player_id': player_id,
            'first_name': first_name,
            'last_name': last_name,
            'avg_fantasy_points': round(avg_fp, 2),
            'consistency_std': round(std_fp, 2),
            'games_played': int(games_played_count),
            'games_missed': int(games_missed_count),
            'variation_pct': round(variation_pct, 2),
            'avg_fantasy_points_l10': round(l10_avg_fp, 2),
            'consistency_std_l10': round(l10_std_fp, 2),
            'variation_pct_l10': round(l10_variation_pct, 2)
        }
        results.append(record)

    logger.info(f"Calculated consistency for {len(results)} players.")
    
    # 4. Upsert to Supabase
    if results:
        logger.info("Upserting consistency records...")
        # Batch upsert just in case
        upsert_batch_size = 100
        for i in range(0, len(results), upsert_batch_size):
            batch = results[i:i + upsert_batch_size]
            res = supabase.table("player_consistency").upsert(batch).execute()
            logger.info(f"Upserted batch {i//upsert_batch_size + 1}")
            
    logger.info("Player Consistency update completed.")

def main():
    update_consistency()

if __name__ == "__main__":
    main()

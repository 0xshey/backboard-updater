-- Create the player_consistency table
CREATE TABLE IF NOT EXISTS public.player_consistency (
    as_of_date date NOT NULL DEFAULT CURRENT_DATE,
    player_id text NOT NULL,
    first_name text,
    last_name text,
    avg_fantasy_points float8,
    consistency_std float8,
    games_played int8,
    games_missed int8,
    variation_pct float8,
    avg_fantasy_points_l10 float8,
    consistency_std_l10 float8,
    variation_pct_l10 float8,
    
    PRIMARY KEY (as_of_date, player_id)
);

-- Enable Row Level Security (RLS) if needed, or leave open as per project standards.
-- ALTER TABLE public.consistency ENABLE ROW LEVEL SECURITY;

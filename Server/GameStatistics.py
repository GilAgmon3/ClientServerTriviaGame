import json
from pathlib import Path


# Utility functions
def load_or_initialize_stats(file_path: str):
    """Load existing statistics from a file or initialize a new one if it doesn't exist."""
    stats_path = Path(file_path)
    if stats_path.exists():
        with open(stats_path, 'r') as file:
            stats = {json.loads(line)['name']: json.loads(line) for line in file if line.strip()}
    else:
        stats = {}
    return stats


def write_individual_stat_to_file(stat: dict, file_path: str):
    """Write or update an individual player's statistics to the file."""
    stats = load_or_initialize_stats(file_path)
    stats[stat['name']] = stat  # Update or add the individual player's stats
    with open(file_path, 'w') as file:  # Overwrite the file with updated stats
        for player_stat in stats.values():
            file.write(json.dumps(player_stat) + '\n')


# Update function for game statistics
def update_stats_per_game(file_path: str, player_name: str, games_played: int, games_won: bool, total_response_time,
                          response_count):
    """Update statistics for a player after a game and write to file."""
    stat = {
        "name": player_name,
        "games_played": games_played,
        "games_won": games_won,
        # "average_response_time": total_response_time / response_count if response_count > 0 else 0
    }
    write_individual_stat_to_file(stat, file_path)

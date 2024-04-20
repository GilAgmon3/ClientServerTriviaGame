import json
from pathlib import Path


# Utility functions
def load_or_initialize_stats(file_path):
    """Load existing statistics from a file or initialize a new one if it doesn't exist."""
    stats_path = Path(file_path)
    if stats_path.exists():
        with open(stats_path, 'r') as file:
            stats = {json.loads(line)['name']: json.loads(line) for line in file if line.strip()}
    else:
        stats = {}
    return stats


def write_stats_to_file(stats, file_path):
    """Write all player statistics to the file, overwriting existing contents."""
    with open(file_path, 'w') as file:
        for stat in stats.values():
            file.write(json.dumps(stat) + '\n')


# Update functions
def update_stats_per_round(stats, player_name, round_won):
    """Update statistics for a player after a round."""
    if player_name not in stats:
        stats[player_name] = {
            "name": player_name,
            "games_played": 0,
            "rounds_participated": 0,
            "rounds_was_right": 0,
            "games_won": 0,
            "total_response_time": 0,
            "response_count": 0,
            "average_response_time": 0.0
        }
    stats[player_name]["rounds_participated"] += 1
    if round_won:
        stats[player_name]["rounds_won"] += 1


def update_stats_per_game(stats, player_name, game_won, response_time):
    """Update statistics for a player after a game."""
    stats[player_name]["games_played"] += 1
    if game_won:
        stats[player_name]["games_won"] += 1
    stats[player_name]["total_response_time"] += response_time
    stats[player_name]["response_count"] += 1
    stats[player_name]["average_response_time"] = (
            stats[player_name]["total_response_time"] / stats[player_name]["response_count"]
    )



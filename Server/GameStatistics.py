import json
from pathlib import Path
from typing import Dict, Any
from Constants import players_statistics_file_path  # Import the file path constant


# Utility functions
def load_or_initialize_stats() -> Dict[str, Any]:
    """Load existing statistics from a JSONL file or initialize a new one if it doesn't exist."""
    stats_path = Path(players_statistics_file_path)
    stats = {}
    if stats_path.exists():
        with open(stats_path, 'r') as file:
            for line in file:
                data = json.loads(line.strip())
                stats[data['name']] = data
    return stats


def write_individual_stat_to_file(stats: Dict[str, Any]):
    """Write all player statistics to the JSONL file, overwriting existing contents."""
    with open(players_statistics_file_path, 'w') as file:
        for player_stat in stats.values():
            file.write(json.dumps(player_stat) + '\n')


def update_stats_per_game(player_name: str, won_game: bool):
    """Update statistics for a player after a game and write to the JSONL file."""
    stats = load_or_initialize_stats()
    player_stat = stats.get(player_name, {
        "name": player_name,
        "games_played": 0,
        "games_won": 0,
        "precision_of_winning": 0
    })

    # Update the statistics
    player_stat["games_played"] += 1
    if won_game:
        player_stat["games_won"] += 1
    player_stat["precision_of_winning"] = player_stat["games_won"] / player_stat["games_played"]

    stats[player_name] = player_stat
    write_individual_stat_to_file(stats)

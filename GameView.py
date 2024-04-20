from Constants import colors


def print_colored(text, color):
    print(f"{colors[color]}{text}{colors['reset']}")

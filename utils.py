import numpy as np
from termcolor import colored
from collections import defaultdict


def parse_instance(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        num_days = int(lines[0].strip())
        num_teams = int(lines[1].strip())
        availabilities = []
        for line in lines[2:]:
            availabilities.append([int(x) for x in line.strip().split()])
    return num_days, num_teams, availabilities


def parse_calendar(file_path):
    predicates = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for home_team, line in enumerate(lines, start=1):
            days = line.strip().split('\t')
            for away_team, day in enumerate(days, start=1):
                day = int(day)
                if day != -1:
                    predicates.append(
                        f'schedule({home_team}, {away_team}, {day}).')

    return predicates


def write_solution(solution, file_path):
    with open(file_path, 'w') as file:
        for line in solution:
            file.write(f"{line}\n")


def build_diff_map(close_games):
    diff_map = defaultdict(lambda: 0)
    for team, time1, time2, diff in close_games:
        diff_map[(team, time1)] = diff
        diff_map[(team, time2)] = diff
    return diff_map


def highlight_matrix(schedule_matrix, diff_map, num_teams):
    highlighted_matrix = []
    for i in range(num_teams):
        row = []
        for j in range(num_teams):
            val = schedule_matrix[i, j]
            if val == -1:
                row.append(colored(f'{val:3}', 'blue'))
            else:
                diff1 = diff_map[(i + 1, val)]
                diff2 = diff_map[(j + 1, val)]
                min_diff = max(diff1, diff2)
                underline = diff1 > 0 and diff2 > 0
                bold = min_diff == 1
                color = 'red' if diff1 > 0 or diff2 > 0 else None
                attrs = ['underline'] if underline else []
                attrs += ['bold'] if bold else []
                row.append(colored(f'{val:3}', color, attrs=attrs))
        highlighted_matrix.append(" ".join(row))
    return highlighted_matrix


def save_matrix_to_file(output_path, model_count, model, solve_duration, schedule_matrix, schedule_atoms, close_games, optimizations, unified_score):
    with open(output_path, 'w') as f:
        f.write(f'Model: {model_count}\n')
        f.write(f'Optimizations: {optimizations}\n')
        f.write(f'Unified Score: {unified_score}\n')
        f.write(f'Time: {solve_duration:.2f}s\n')
        f.write('\nSchedule Matrix:\n')
        for row in schedule_matrix:
            f.write(" ".join(f'{val:3}' for val in row) + '\n')
        f.write('\n\nSchedules:\n')
        for atom in schedule_atoms:
            f.write(f'{atom}\n')
        f.write('\n\nClose Games:\n')
        for game in close_games:
            f.write(f'{game}\n')


def calculate_unified_score(optimization, num_teams):
    max_scheduled_games = num_teams * (num_teams - 1)
    unified_score = (max_scheduled_games +
                     optimization[0]) * 1000 + optimization[1]
    return unified_score

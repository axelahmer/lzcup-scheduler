import csv
from collections import defaultdict
from termcolor import colored

def parse_instance(instance_number):
    instance_file = f"data/instances/Input{instance_number}.txt"
    with open(instance_file, 'r') as file:
        lines = file.readlines()
        num_days = int(lines[0].strip())
        num_teams = int(lines[1].strip())
        availabilities = [[int(x) for x in line.strip().split()] for line in lines[2:]]
    
    predicates = []
    for day in range(num_days):
        predicates.append(f"time({day}).")
    for team in range(1, num_teams + 1):
        predicates.append(f"team({team}).")
    
    for day, day_availabilities in enumerate(availabilities):
        for team, status in enumerate(day_availabilities, start=1):
            if status == 1:
                predicates.append(f"home({team},{day}).")
            elif status == 2:
                predicates.append(f"forbidden({team},{day}).")
    
    return num_days, num_teams, predicates

def parse_calendar(calendar_path):
    predicates = []
    with open(calendar_path, 'r') as file:
        for home_team, line in enumerate(file, start=1):
            days = line.strip().split('\t')
            for away_team, day in enumerate(days, start=1):
                day = int(day)
                if day != -1:
                    predicates.append(f'schedule({home_team}, {away_team}, {day}).')
    return predicates

def calculate_unified_score(optimization, num_teams):
    max_scheduled_games = num_teams * (num_teams - 1)
    unified_score = (max_scheduled_games + optimization[0]) * 1000 + optimization[1]
    return unified_score

CSV_HEADERS = [
    'timestamp', 'run_name', 'instance', 'rmax', 'm', 'threads', 'config', 'heuristic', 'timeout',
    'model', 'time', 'opt1', 'opt2', 'score', 'schedule', 'close_games', 'optimal'
]

def write_csv_row(csv_writer, data):
    csv_writer.writerow([data[header] for header in CSV_HEADERS])

def format_schedule_matrix(schedule_matrix):
    return ';'.join([','.join(map(str, row)) for row in schedule_matrix])

def format_close_games(close_games):
    return ';'.join([f'{t},{t1},{t2},{d}' for t, t1, t2, d in close_games])

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
            val = schedule_matrix[i][j]
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
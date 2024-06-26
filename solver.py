import csv
import os
from datetime import datetime
import argparse
import clingo
import time
from utils import parse_instance, parse_calendar, calculate_unified_score, write_csv_row, format_schedule_matrix, format_close_games, build_diff_map, highlight_matrix, CSV_HEADERS

def report_model(model, num_teams, solve_start_time, meta_info, csv_writer, render):
    solve_duration = time.time() - solve_start_time

    optimizations = model.cost
    unified_score = calculate_unified_score(optimizations, num_teams)

    schedule_matrix = [[-1 for _ in range(num_teams)] for _ in range(num_teams)]
    close_games = []

    for atom in model.symbols(atoms=True):
        if atom.name == "schedule":
            home_team, away_team, day = [arg.number for arg in atom.arguments]
            schedule_matrix[home_team - 1][away_team - 1] = day
        elif atom.name == "close_game":
            team, time1, time2, diff = [arg.number for arg in atom.arguments]
            close_games.append((team, time1, time2, diff))

    data = {
        'timestamp': meta_info['timestamp'],
        'run_name': meta_info['run_name'],
        'instance': meta_info['instance_number'],
        'rmax': meta_info['rmax'],
        'm': meta_info['m'],
        'threads': meta_info['threads'],
        'config': meta_info['configuration'],
        'heuristic': meta_info['use_heuristic'],
        'timeout': meta_info['timeout'],
        'model': model.number,
        'time': solve_duration,
        'opt1': optimizations[0],
        'opt2': optimizations[1],
        'score': unified_score,
        'schedule': format_schedule_matrix(schedule_matrix),
        'close_games': format_close_games(close_games),
        'optimal': model.optimality_proven
    }

    write_csv_row(csv_writer, data)

    print(f"Model {model.number:<4d} : {solve_duration:>6.2f}s : {unified_score:>7d}  {optimizations}  {'*opt*' if model.optimality_proven else ''}")

    if render:
        diff_map = build_diff_map(close_games)
        matrix_output = highlight_matrix(schedule_matrix, diff_map, num_teams)
        for row in matrix_output:
            print(row)
        print()  # Extra line for spacing

def solve_instance(instance_number, rmax, m, threads, output_dir, configuration, timeout, run_name, use_heuristic, render=False, calendar_path=None):
    num_days, num_teams, predicates = parse_instance(instance_number)
    if calendar_path:
        predicates.extend(parse_calendar(calendar_path))

    clingo_args = [
        f"-t {threads}",
        f"-c rmax={rmax}",
        f"-c m={m}",
        f'-c n={num_teams}',
        f"--configuration={configuration}",
        "--opt-mode=optN",
        "-n 1"
    ]
    
    if use_heuristic:
        clingo_args.append("--heuristic=Domain")

    control = clingo.Control(arguments=clingo_args)
    control.load("lzcup.lp")

    for predicate in predicates:
        control.add("base", [], predicate)

    control.ground([("base", [])])

    solve_start_time = time.time()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'results.csv')
    
    file_exists = os.path.isfile(csv_path)
    
    with open(csv_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        if not file_exists:
            csv_writer.writerow(CSV_HEADERS)
        meta_info = {
            'timestamp': timestamp,
            'run_name': run_name,
            'instance_number': instance_number,
            'rmax': rmax,
            'm': m,
            'threads': threads,
            'configuration': configuration,
            'use_heuristic': use_heuristic,
            'timeout': timeout,
        }
        
        print(f"\n{'-'*50}")
        print(f"Instance: {instance_number:3d}")
        print(f"Rmax: {rmax:2d} | M: {m:3d} | Threads: {threads:2d}")
        print(f"Config: {configuration:5s} | Heuristic: {str(use_heuristic):5s}")
        print(f"Timeout: {timeout:4d}s")
        print(f"{'-'*50}\n")

        with control.solve(on_model=lambda m: report_model(m, num_teams, solve_start_time, meta_info, csv_writer, render), async_=True) as handle:
            handle.wait(timeout)
            handle.cancel()

    print()  # New line after progress output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indoor Football Scheduling")
    parser.add_argument("i", type=int, help="Instance number to solve")
    parser.add_argument("-r", "--rmax", type=int, default=4, help="Maximum range for close games (default: 4)")
    parser.add_argument("-m", type=int, default=60, help="Minimum time slots between same team games (default: 60)")
    parser.add_argument("-t", "--threads", type=int, default=2, help="Number of threads to use (default: 2)")
    parser.add_argument("-o", "--output", type=str, default='results', help="Directory to save output files (default: results)")
    parser.add_argument("-c", "--config", type=str, default='auto', help="Configuration for clingo (default: auto)")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds (default: 60)")
    parser.add_argument("-n", "--name", type=str, default="default_run", help="Name of the run for identification")
    parser.add_argument("--heuristic", action="store_true", help="Use Domain heuristic")
    parser.add_argument("--render", action="store_true", help="Render the schedule matrix for each model")
    parser.add_argument("--calendar", type=str, help="Path to calendar file to validate")
    args = parser.parse_args()

    solve_instance(args.i, args.rmax, args.m, args.threads, args.output, args.config, args.timeout, args.name, args.heuristic, args.render, args.calendar)
from utils import parse_instance, parse_calendar, write_solution, build_diff_map, highlight_matrix, save_matrix_to_file, calculate_unified_score
from datetime import datetime
from functools import partial
from collections import defaultdict
import matplotlib.pyplot as plt
import sys
import argparse
import clingo
import numpy as np
from termcolor import colored
import time
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend


def report_model(model, num_teams, model_count, solve_start_time, meta_info, output_dir):
    model_count[0] += 1
    solve_end_time = time.time()
    solve_duration = solve_end_time - solve_start_time

    optimizations = model.cost
    unified_score = calculate_unified_score(optimizations, num_teams)

    print(f'\nModel {model_count[0]}:')
    print(f'  Optimizations: {optimizations}')
    print(f'  Unified Score: {unified_score}')
    print(f'  Time: {solve_duration:.2f}s')

    schedule_matrix = np.full((num_teams, num_teams), -1)
    close_games = []

    atoms = model.symbols(atoms=True)
    schedule_atoms = []
    for atom in atoms:
        if atom.name == "schedule":
            home_team, away_team, day = [arg.number for arg in atom.arguments]
            schedule_matrix[home_team - 1, away_team - 1] = day
            schedule_atoms.append(f'schedule({home_team}, {away_team}, {day})')
        elif atom.name == "close_game":
            team, time1, time2, diff = [arg.number for arg in atom.arguments]
            close_games.append((team, time1, time2, diff))

    diff_map = build_diff_map(close_games)

    matrix_output = highlight_matrix(schedule_matrix, diff_map, num_teams)
    for row in matrix_output:
        print(row)

    output_filename = f'model_{model_count[0]}_opt_{optimizations}_score_{
        unified_score}_time_{solve_duration:.2f}.txt'
    output_path = os.path.join(output_dir, output_filename)
    save_matrix_to_file(output_path, model_count[0], model, solve_duration,
                        schedule_matrix, schedule_atoms, close_games, optimizations, unified_score)

    meta_info['times'].append(solve_duration)
    meta_info['optimizations'].append(optimizations)
    meta_info['unified_scores'].append(unified_score)

    # Update plots after each model
    plot_unified_score(meta_info['times'],
                       meta_info['unified_scores'], output_dir)
    plot_optimization(meta_info['times'],
                      meta_info['optimizations'], 0, output_dir)
    plot_optimization(meta_info['times'],
                      meta_info['optimizations'], 1, output_dir)


def plot_unified_score(times, unified_scores, output_dir):
    plt.figure(figsize=(10, 6))
    plt.plot(times, unified_scores, marker='o', label='Unified Score')
    plt.xlabel('Time (s)')
    plt.ylabel('Unified Score')
    plt.title('Unified Score over time')
    plt.grid(True)
    plt.legend()
    plt.yscale('log')  # Set the y-axis to use a logarithmic scale
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'unified_score_plot.png'))
    plt.close()


def plot_optimization(times, optimizations, index, output_dir):
    plt.figure(figsize=(10, 6))
    plt.plot(times, [opt[index] for opt in optimizations],
             marker='o', label=f'Optimization {index+1}')
    plt.xlabel('Time (s)')
    plt.ylabel(f'Optimization {index+1}')
    plt.title(f'Optimization {index+1} over time')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'optimization{index+1}_plot.png'))
    plt.close()


def main(instance_number, rmax, m, threads, output_dir, configuration, calendar_path=None):
    if calendar_path:
        schedule_predicates = parse_calendar(calendar_path)

    instance_file = f"data/instances/Input{instance_number}.txt"
    num_days, num_teams, availabilities = parse_instance(instance_file)

    control = clingo.Control(
        arguments=[f"-t {threads}", f"-c rmax={rmax}", f"-c m={m}", f'-c n={num_teams}', f"--configuration={configuration}"])
    control.load("lzcup.lp")

    for day in range(num_days):
        control.add("base", [], f"time({day}).")
    for team in range(1, num_teams + 1):
        control.add("base", [], f"team({team}).")

    for day in range(num_days):
        for team in range(1, num_teams + 1):
            status = availabilities[day][team - 1]
            if status == 1:
                control.add("base", [], f"home({team},{day}).")
            if status == 2:
                control.add("base", [], f"forbidden({team},{day}).")

    if calendar_path:
        for predicate in schedule_predicates:
            control.add("base", [], predicate)

    control.ground([("base", [])])

    model_count = [0]
    solve_start_time = time.time()

    meta_info = {'times': [], 'optimizations': [], 'unified_scores': []}

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(output_dir, str(instance_number), timestamp)
    os.makedirs(output_dir, exist_ok=True)

    report_model_partial = partial(report_model, num_teams=num_teams, model_count=model_count,
                                   solve_start_time=solve_start_time, meta_info=meta_info, output_dir=output_dir)
    result = control.solve(on_model=report_model_partial)

    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indoor Football Scheduling")
    parser.add_argument("instance_number", type=int,
                        help="Instance number to solve")
    parser.add_argument("rmax", type=int, help="Maximum range for close games")
    parser.add_argument(
        "m", type=int, help="Minimum time slots between same team games")
    parser.add_argument("--threads", type=int, default=4,
                        help="Number of threads to use (default: 4)")
    parser.add_argument("--output_dir", type=str,
                        default='output', help="Directory to save output files")
    parser.add_argument("--configuration", type=str, default='auto',
                        help="Configuration for clingo (default: auto)")
    parser.add_argument("--calendar_path", type=str,
                        help="Path to calendar file to validate")
    args = parser.parse_args()

    main(args.instance_number, args.rmax, args.m,
         args.threads, args.output_dir, args.configuration, args.calendar_path)

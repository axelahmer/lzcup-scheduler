# LZV Cup Scheduling in Clingo!

This repository contains an Answer Set Programming (ASP) implementation using Clingo for scheduling the LZV Cup, an amateur indoor football league in Belgium.

## Overview

The LZV Cup is a time-relaxed double round-robin tournament where each team plays against every other team twice, once at home and once away. The main goal is to generate a schedule that balances the rest days between matches for each team to avoid close succession of games.

## Repository Structure

- `lzcup.lp`: The main ASP file containing the problem encoding and constraints.
- `data/instances/`: Directory containing the input instances in text format.
- `data/calendars/gurobi/`: Directory containing Gurobi-generated calendars for validation.
- `solver.py`: Python script to solve the scheduling problem and report results.
- `run_batch.py`: Python script to run a batch of instances.
- `utils.py`: Helper functions used by `solver.py` and `run_batch.py`.

## Input Instance Format

The input instances are located in the `data/instances/` directory. Each instance file has the following format:

- First line: Total number of days in the season.
- Second line: Total number of teams in the league.
- Subsequent lines: Team availabilities, where each column represents a team, and each row represents a time slot. A "1" indicates that the slot is in the home game set of the team, a "2" means the slot is in the forbidden game set, and "0" means that the team can play an away match.

## Output Schedule Format

The generated schedules are saved in the results CSV file. Each schedule is represented in the following format within the CSV:

- Each row represents a home team, and each column represents an away team.
- The cell (i, j) stores the time slot in which home team i plays against away team j.
- A "-1" indicates that the match could not be scheduled.

## Interpreting the Console Output

The console output displays the generated schedule matrix with additional formatting to highlight close games:

- Red bold numbers: Back-to-back games for a team.
- Red numbers: Games within 3 time slots of another game for a team.
- Underlined numbers: Both teams playing in the scheduled match have close games paired with that match.
- Blue numbers: Unscheduled matches, represented by "-1".

## Usage

### solver.py

The `solver.py` script solves a single instance of the scheduling problem. 

#### Command:
```
python solver.py <instance_number> <rmax> <m> [--threads <num_threads>] [--output_dir <output_directory>] [--configuration <clingo_configuration>] [--calendar_path <path_to_calendar>] [--timeout <timeout>] [--name <run_name>] [--heuristic] [--render]
```

#### Parameters:

- `<instance_number>`: (int) The number of the input instance file.
- `<rmax>`: (int) The maximum range for close games.
- `<m>`: (int) The minimum number of time slots between games with the same teams.
- `--threads`: (Optional) (int) The number of threads to use for solving (default: 4).
- `--output_dir`: (Optional) (str) The directory to save the output files (default: "output").
- `--configuration`: (Optional) (str) The configuration for Clingo (default: "auto").
- `--calendar_path`: (Optional) (str) Path to an external calendar file for validation.
- `--timeout`: (Optional) (int) Timeout in seconds (default: 60).
- `--name`: (Optional) (str) Name of the run for identification (default: "default_run").
- `--heuristic`: (Optional) Use Domain heuristic.
- `--render`: (Optional) Render the schedule matrix for each model.

### run_batch.py

The `run_batch.py` script runs a batch of instances. 

#### Command:
```
python run_batch.py <instance_lower> <instance_upper> [--rmax <rmax>] [--m <m>] [--threads <num_threads>] [--output_dir <output_directory>] [--configuration <clingo_configuration>] [--timeout <timeout>] [--name <run_name>] [--heuristic] [--render] [--calendar <path_to_calendar>]
```

#### Parameters:

- `<instance_lower>`: (int) The lower bound of instance numbers to solve.
- `<instance_upper>`: (int) The upper bound of instance numbers to solve.
- `--rmax`: (Optional) (int) The maximum range for close games (default: 4).
- `--m`: (Optional) (int) The minimum number of time slots between games with the same teams (default: 60).
- `--threads`: (Optional) (int) The number of threads to use for solving (default: 2).
- `--output_dir`: (Optional) (str) The directory to save the output files (default: "results").
- `--configuration`: (Optional) (str) The configuration for Clingo (default: "auto").
- `--timeout`: (Optional) (int) Timeout in seconds (default: 60).
- `--name`: (Required) (str) Name of the batch run for identification.
- `--heuristic`: (Optional) Use Domain heuristic.
- `--render`: (Optional) Render the schedule matrix for each model.
- `--calendar`: (Optional) (str) Path to calendar file to validate.

## References

Van Bulck, D., Goossens, D.R. & Spieksma, F.C.R. (2019). Scheduling a non-professional indoor football league: a tabu search based approach. Annals of Operations Research, 275:715-730.
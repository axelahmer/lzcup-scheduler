# LZV Cup Scheduling in Clingo!

This repository contains an Answer Set Programming (ASP) implementation using Clingo for scheduling the LZV Cup, an amateur indoor football league in Belgium.

## Overview

The LZV Cup is a time-relaxed double round-robin tournament where each team plays against every other team twice, once at home and once away. The main goal is to generate a schedule that balances the rest days between matches for each team to avoid close succession of games.

## Repository Structure

- `lzcup.lp`: The main ASP file containing the problem encoding and constraints.
- `data/instances/`: Directory containing the input instances in text format.
- `output/`: Directory where the generated schedules and visualizations are stored.
- `lzcup.py`: Python script to run the scheduling program and visualize the results.
- `utils.py`: Helper functions used by `lzcup.py`.

## Input Instance Format

The input instances are located in the `data/instances/` directory. Each instance file has the following format:

- First line: Total number of days in the season.
- Second line: Total number of teams in the league.
- Subsequent lines: Team availabilities, where each column represents a team, and each row represents a time slot. A "1" indicates that the slot is in the home game set of the team, a "2" means the slot is in the forbidden game set, and "0" means that the team can play an away match.

## Output Schedule Format

The generated schedules are saved in the `output/` directory. Each schedule file has the following format:

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

1. Install Clingo and the required Python dependencies.
2. Place the input instances in the `data/instances/` directory.
3. Run `python lzcup.py <instance_number> <rmax> <m> [--threads <num_threads>] [--output_dir <output_directory>] [--configuration <clingo_configuration>]` to generate the schedule for the specified instance.
   - `<instance_number>`: The number of the input instance file.
   - `<rmax>`: The maximum range for close games.
   - `<m>`: The minimum number of time slots between games with the same teams.
   - `--threads`: (Optional) The number of threads to use for solving (default: 4).
   - `--output_dir`: (Optional) The directory to save the output files (default: "output").
   - `--configuration`: (Optional) The configuration for Clingo (default: "auto").

## References

Van Bulck, D., Goossens, D.R. & Spieksma, F.C.R. (2019). Scheduling a non-professional indoor football league: a tabu search based approach. Annals of Operations Research, 275:715-730.
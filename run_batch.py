import argparse
from solver import solve_instance

def run_batch(instance_lower, instance_upper, rmax, m, threads, output_dir, configuration, timeout, run_name, use_heuristic, render, calendar_path=None):
    print(f"Batch run: {run_name}")
    print(f"Instances: {instance_lower}-{instance_upper}")
    print(f"Output directory: {output_dir}")
    print()

    for instance in range(instance_lower, instance_upper + 1):
        solve_instance(instance, rmax, m, threads, output_dir, configuration, timeout, run_name, use_heuristic, render, calendar_path)

    print(f"Batch run {run_name} completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a batch of instances for Indoor Football Scheduling")
    parser.add_argument("il", type=int, help="Lower bound of instance numbers to solve")
    parser.add_argument("iu", type=int, help="Upper bound of instance numbers to solve")
    parser.add_argument("-r", "--rmax", type=int, default=4, help="Rmax value to use (default: 4)")
    parser.add_argument("-m", type=int, default=60, help="M value to use (default: 60)")
    parser.add_argument("-t", "--threads", type=int, default=2, help="Number of threads to use (default: 2)")
    parser.add_argument("-c", "--config", type=str, default="auto", help="Clingo configuration to use (default: auto)")
    parser.add_argument("-o", "--output", type=str, default='results', help="Directory to save output files (default: results)")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds for each run (default: 60)")
    parser.add_argument("-n", "--name", type=str, required=True, help="Name of the batch run for identification")
    parser.add_argument("--heuristic", action="store_true", help="Use Domain heuristic")
    parser.add_argument("--render", action="store_true", help="Render the schedule matrix for each model")
    parser.add_argument("--calendar", type=str, help="Path to calendar file to validate")
    
    args = parser.parse_args()
    
    run_batch(args.il, args.iu, args.rmax, args.m, args.threads, 
              args.output, args.config, args.timeout, args.name, args.heuristic, args.render, args.calendar)
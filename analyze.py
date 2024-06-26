import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
import os
import argparse

def load_data(file_path):
    return pd.read_csv(file_path)

def add_baseline_to_data(df, gurobi_scores, tabu_scores):
    gurobi_df = pd.DataFrame({
        'instance': range(1, len(gurobi_scores) + 1),
        'run_name': 'GUROBI',
        'score': gurobi_scores
    })
    tabu_df = pd.DataFrame({
        'instance': range(1, len(tabu_scores) + 1),
        'run_name': 'TABU',
        'score': tabu_scores
    })
    return pd.concat([df, gurobi_df, tabu_df], ignore_index=True)

def calculate_relative_performance(df):
    best_scores = df.groupby(['instance', 'run_name'])['score'].min().reset_index()
    gurobi_scores = best_scores[best_scores['run_name'] == 'GUROBI'].set_index('instance')['score']
    
    merged_scores = best_scores.merge(gurobi_scores, on='instance', suffixes=('', '_gurobi'))
    merged_scores['relative_to_gurobi'] = merged_scores['score'] / merged_scores['score_gurobi']
    merged_scores['relative_to_gurobi'] = merged_scores['relative_to_gurobi'].replace([np.inf, -np.inf], np.nan)
    return merged_scores

def create_bar_plot(data, output_path):
    plt.figure(figsize=(20, 10))
    run_names = ['GUROBI', 'TABU'] + sorted(data[~data['run_name'].isin(['GUROBI', 'TABU'])]['run_name'].unique().tolist())
    colors = ['blue', 'red'] + sns.color_palette(n_colors=len(run_names)-2)
    
    ax = sns.barplot(x='instance', y='score', hue='run_name', data=data, hue_order=run_names, palette=dict(zip(run_names, colors)))
    plt.xlabel('Instance')
    plt.ylabel('Score (lower is better)')
    plt.title('Performance of Runs Including GUROBI and TABU')
    plt.legend(title='Run Name', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.yscale('log')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_pie_chart(data, labels, title, output_path):
    plt.figure(figsize=(12, 8))
    plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title(title)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_heatmap(data, output_path):
    plt.figure(figsize=(20, 12))
    sns.heatmap(data, cmap='YlOrRd', annot=False, fmt='.2f', cbar_kws={'label': 'Relative to Best Score'})
    plt.title('Heatmap of Run Performance Relative to Best Score')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_box_plot(data, output_path):
    plt.figure(figsize=(12, 6))
    run_names = ['GUROBI', 'TABU'] + sorted(data[~data['run_name'].isin(['GUROBI', 'TABU'])]['run_name'].unique().tolist())
    colors = ['blue', 'red'] + sns.color_palette(n_colors=len(run_names)-2)
    
    sns.boxplot(x='run_name', y='score', data=data, order=run_names, hue='run_name', palette=dict(zip(run_names, colors)))
    plt.xlabel('Run Name')
    plt.ylabel('Score (lower is better)')
    plt.title('Distribution of Scores Across Instances')
    plt.yscale('log')
    plt.xticks(rotation=45)
    plt.legend([],[], frameon=False)  # Remove legend as it's redundant with x-axis labels
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def get_best_runs(data):
    # Find the minimum score for each instance
    min_scores = data.groupby('instance')['score'].min().reset_index()
    min_scores = min_scores.rename(columns={'score': 'min_score'})
    
    # Merge the minimum scores back to the original data
    merged = data.merge(min_scores, on='instance')
    
    # Filter for rows where score equals min_score and aggregate run names
    best_runs = merged[merged['score'] == merged['min_score']].groupby('instance').agg({
        'run_name': lambda x: ', '.join(sorted(x)),
        'min_score': 'first'
    }).reset_index()
    
    return best_runs

def analyze_runs(df, gurobi_scores, tabu_scores, run_names=None, output_dir='results'):
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)

    df = add_baseline_to_data(df, gurobi_scores, tabu_scores)
    
    if run_names:
        run_names = ['GUROBI', 'TABU'] + run_names
        df = df[df['run_name'].isin(run_names)]

    best_scores = df.groupby(['instance', 'run_name'])['score'].min().reset_index()

    create_bar_plot(best_scores, os.path.join(plots_dir, 'run_comparison_bar_plot.png'))
    create_box_plot(best_scores, os.path.join(plots_dir, 'scores_distribution_box_plot.png'))

    relative_performance = calculate_relative_performance(df)
    avg_relative_performance = relative_performance.groupby('run_name')['relative_to_gurobi'].mean().sort_values()
    print("\nAverage performance relative to GUROBI (lower is better, 1.0 means equal to GUROBI):")
    print(avg_relative_performance)

    best_runs = get_best_runs(best_scores)
    run_counts = best_runs['run_name'].str.split(', ', expand=True).stack().value_counts()

    print("\nNumber of times each run was among the best (including ties):")
    print(run_counts)

    create_pie_chart(run_counts.values, run_counts.index, 'Distribution of Best Runs (including ties)', 
                     os.path.join(plots_dir, 'best_runs_pie_chart.png'))

    print("\nBest run(s) for each instance:")
    for _, row in best_runs.iterrows():
        print(f"Instance {row['instance']}: {row['run_name']}")

    pivot_data = best_scores.pivot(index='instance', columns='run_name', values='score')
    best_scores = pivot_data.min(axis=1)
    relative_to_best = pivot_data.div(best_scores, axis=0)
    create_heatmap(relative_to_best, os.path.join(plots_dir, 'relative_performance_heatmap.png'))

    print("\nData statistics:")
    print(f"Number of unique instances: {len(best_scores.index)}")
    print(f"Number of unique runs: {len(pivot_data.columns)}")

    print("Analysis complete. Visualizations saved in the results/plots folder.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze and compare run results for indoor football scheduling")
    parser.add_argument("-r", "--runs", nargs="*", help="Specific run names to analyze. If not provided, all runs will be analyzed.")
    parser.add_argument("-o", "--output", default="results", help="Output directory for results and plots (default: results)")
    args = parser.parse_args()

    gurobi_scores = [2087, 80, 58, 54, 52, 39, 38, 1036, 35, 28, 22, 20, 16, 1013, 13, 8, 7, 6, 5, 5, 2004, 4, 4, 4, 4, 4, 3, 3, 3, 2, 1001, 1, 1, 3000, 1000, 1000, 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    tabu_scores = [2087, 81, 58, 54, 66, 39, 41, 1036, 39, 29, 32, 20, 18, 1015, 13, 8, 7, 6, 5, 5, 2004, 6, 4, 4, 4, 4, 8, 3, 3, 4, 1001, 1, 1, 3000, 1000, 1000, 1000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    df = load_data('results/results.csv')
    
    print(f"Analyzing {'specified' if args.runs else 'all'} runs")
    
    analyze_runs(df, gurobi_scores, tabu_scores, args.runs, args.output)
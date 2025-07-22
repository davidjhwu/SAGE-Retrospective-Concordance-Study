import json
import matplotlib.pyplot as plt
import numpy as np

def load_data(jsonl_file):
    data = []
    with open(jsonl_file, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def create_scatter_plot_4panel(jsonl_file, output_file='scatterplot_4panel.png'):
    data = load_data(jsonl_file)
    
    supported_counts = []
    not_supported_counts = []
    concordance_best_of_3 = []
    concordance_vishnu = []
    concordance_saloni = []
    concordance_jessica = []
    dav_ids = []
    
    for entry in data:
        supported_counts.append(entry['Supported'])
        not_supported_counts.append(entry['Not Supported'])
        concordance_best_of_3.append(float(entry['Concordance']))
        concordance_vishnu.append(float(entry['Concordance_Vishnu']))
        concordance_saloni.append(float(entry['Concordance_Saloni']))
        concordance_jessica.append(float(entry['Concordance_Jessica']))
        dav_ids.append(entry['dav_id'])
    
    # Create 2x2 subplot figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Supported vs Unsupported Claims by Concordance Measure', fontsize=16)
    
    concordance_data = [
        (concordance_best_of_3, 'Best-of-3 Vote'),
        (concordance_vishnu, 'Vishnu'),
        (concordance_saloni, 'Saloni'),
        (concordance_jessica, 'Jessica')
    ]
    
    for idx, (concordance_values, title) in enumerate(concordance_data):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        colors = ['blue' if concordance == 1.0 else 'orange' for concordance in concordance_values]
        
        # Add small random jitter to avoid overlapping points
        supported_jitter = [x + np.random.normal(0, 0.1) for x in supported_counts]
        not_supported_jitter = [y + np.random.normal(0, 0.1) for y in not_supported_counts]
        
        ax.scatter(supported_jitter, not_supported_jitter, c=colors, alpha=0.7, s=50)
        
        ax.set_xlabel('Number of Supported Claims')
        ax.set_ylabel('Number of Unsupported Claims')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        concordant_count = sum(1 for c in concordance_values if c == 1.0)
        not_concordant_count = sum(1 for c in concordance_values if c == 0.0)
        
        blue_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label=f'Concordant (n={concordant_count})')
        orange_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=8, label=f'Not Concordant (n={not_concordant_count})')
        ax.legend(handles=[blue_patch, orange_patch], fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"4-panel scatter plot saved as {output_file}")
    print(f"Total cases: {len(data)}")
    for concordance_values, title in concordance_data:
        concordant = sum(1 for c in concordance_values if c == 1.0)
        not_concordant = sum(1 for c in concordance_values if c == 0.0)
        print(f"{title} - Concordant: {concordant}, Not Concordant: {not_concordant}")

def create_scatter_plot(jsonl_file, output_file='scatterplot.png'):
    data = load_data(jsonl_file)
    
    supported_counts = []
    not_supported_counts = []
    concordance_values = []
    dav_ids = []
    
    for entry in data:
        supported_counts.append(entry['Supported'])
        not_supported_counts.append(entry['Not Supported'])
        concordance_values.append(float(entry['Concordance']))
        dav_ids.append(entry['dav_id'])
    
    colors = ['blue' if concordance == 1.0 else 'orange' for concordance in concordance_values]
    
    # Add small random jitter to avoid overlapping points
    supported_jitter = [x + np.random.normal(0, 0.1) for x in supported_counts]
    not_supported_jitter = [y + np.random.normal(0, 0.1) for y in not_supported_counts]
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(supported_jitter, not_supported_jitter, c=colors, alpha=0.7, s=60)
    
    plt.xlabel('Number of Supported Claims')
    plt.ylabel('Number of Unsupported Claims')
    plt.title('Supported vs Unsupported Claims by Case')
    plt.grid(True, alpha=0.3)
    
    concordant_count = sum(1 for c in concordance_values if c == 1.0)
    not_concordant_count = sum(1 for c in concordance_values if c == 0.0)
    
    blue_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label=f'Concordant (n={concordant_count})')
    orange_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=8, label=f'Not Concordant (n={not_concordant_count})')
    plt.legend(handles=[blue_patch, orange_patch])
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Scatter plot saved as {output_file}")
    print(f"Total cases: {len(data)}")
    print(f"Concordance = 1: {sum(1 for c in concordance_values if c == 1.0)}")
    print(f"Concordance = 0: {sum(1 for c in concordance_values if c == 0.0)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        jsonl_file = sys.argv[1]
    else:
        jsonl_file = '../test_results_gpt4.1/final_output.jsonl'
    
    # Create both single plot and 4-panel plot
    create_scatter_plot(jsonl_file)
    create_scatter_plot_4panel(jsonl_file)
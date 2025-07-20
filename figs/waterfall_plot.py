import json
import matplotlib.pyplot as plt
import os

# Path to the results file
results_path = os.path.join(os.path.dirname(__file__), '../test_results_gpt4.1/final_output.jsonl')

# Read the data
raw_data = []
with open(results_path, 'r') as f:
    for line in f:
        entry = json.loads(line)
        # Convert support_percentage and not_addressed_percentage to float (strip % if present)
        support_perc = entry['support_percentage']
        if isinstance(support_perc, str) and support_perc.endswith('%'):
            support_perc = float(support_perc.strip('%'))
        else:
            support_perc = float(support_perc)
        not_addr_perc = entry['not_addressed_percentage']
        if isinstance(not_addr_perc, str) and not_addr_perc.endswith('%'):
            not_addr_perc = float(not_addr_perc.strip('%'))
        else:
            not_addr_perc = float(not_addr_perc)
        concordance = entry.get('Concordance', None)
        raw_data.append({
            'dav_id': entry['dav_id'],
            'support_percentage': support_perc,
            'support_fraction': entry['support_fraction'],
            'not_addressed_percentage': not_addr_perc,
            'not_addressed_fraction': entry['not_addressed_fraction'],
            'Concordance': concordance
        })

# Sort by support_percentage ascending
sorted_data = sorted(raw_data, key=lambda x: x['support_percentage'])

# Prepare data for plotting
support_percentages = [d['support_percentage'] for d in sorted_data]
support_fractions = [d['support_fraction'] for d in sorted_data]
not_addressed_percentages = [d['not_addressed_percentage'] for d in sorted_data]
not_addressed_fractions = [d['not_addressed_fraction'] for d in sorted_data]
concordances = [d['Concordance'] for d in sorted_data]

def get_color(conc):
    if conc == 1.0:
        return 'green'
    elif conc == 0.0:
        return 'red'
    else:
        return 'skyblue'

n = len(support_percentages)
ind = range(n)
bar_width = 0.5

plt.figure(figsize=(14, 7))
# Support bars (above x-axis)
support_colors = [get_color(c) for c in concordances]
bars1 = plt.bar(
    ind,
    support_percentages,
    width=bar_width,
    color=support_colors,
    edgecolor=support_colors,  # Add this line
    label='Supported'
)
# Not Addressed bars (below x-axis, as negative values)
not_addr_edgecolors = [get_color(c) for c in concordances]
bars2 = plt.bar(ind, [-v for v in not_addressed_percentages], width=bar_width, color='none', edgecolor=not_addr_edgecolors, label='Not Addressed (outline)')

plt.xlabel('dav_id')
plt.ylabel('Percentage')
plt.title('Waterfall Plot of SAGE Cases by % Supported Claims (Rated by Saloni)')
# Set dav_id as x-tick labels, 30 degree rotation, font size 6, no tick marks
plt.xticks(ind, [d['dav_id'] for d in sorted_data], rotation=30, fontsize=6)
plt.tick_params(axis='x', length=0)  # Remove tick marks
# Custom legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='green', edgecolor='green', label='Concordant'),
    Patch(facecolor='red', edgecolor='red', label='Not Concordant'),
    Patch(facecolor='skyblue', edgecolor='skyblue', label='Not Rated'),
    Patch(facecolor='none', edgecolor='black', label='Not Addressed (outline)')
]
plt.legend(handles=legend_elements, loc='center right')
plt.tight_layout()

# Annotate each bar with its fraction
for idx, (bar1, bar2) in enumerate(zip(bars1, bars2)):
    # Support fraction above support bar
    height1 = bar1.get_height()
    num1, denom1 = support_fractions[idx].split('/')
    latex_frac1 = rf"${{\frac{{{num1.strip()}}}{{{denom1.strip()}}}}}$"
    plt.text(bar1.get_x() + bar1.get_width()/2, height1 + 1, latex_frac1,
             ha='center', va='bottom', fontsize=8, rotation=0)
    # Not addressed fraction below not addressed bar
    height2 = bar2.get_height()
    num2, denom2 = not_addressed_fractions[idx].split('/')
    latex_frac2 = rf"${{\frac{{{num2.strip()}}}{{{denom2.strip()}}}}}$"
    plt.text(bar2.get_x() + bar2.get_width()/2, height2 - 3, latex_frac2,
             ha='center', va='top', fontsize=8, rotation=0)
# Set dav_id as x-tick labels, horizontally, under the x-axis
# plt.xticks(ind, [d['dav_id'] for d in sorted_data], rotation=0, fontsize=8) # This line is now redundant

# Add horizontal dotted line at y = 80%
plt.axhline(y=80, color='gray', linestyle=':', alpha=0.7, linewidth=1, label='80% threshold')

# Adjust y-limits for clarity
plt.ylim(min(-max(not_addressed_percentages) - 10, -20), max(support_percentages) + 10)

# Save the figure
plt.savefig(os.path.join(os.path.dirname(__file__), 'waterfall_plot.png'))
plt.show() 
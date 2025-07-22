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
    if conc in [1, 1.0, "1.0"]:
        return 'blue'
    elif conc in [0, 0.0, "0.0"]:
        return 'orange'
    else:
        return 'gray'

n = len(support_percentages)
ind = range(n)
bar_width = 0.5

# Create first figure: Support bars only
plt.figure(figsize=(9, 5))
support_colors = [get_color(c) for c in concordances]
bars1 = plt.bar(
    ind,
    support_percentages,
    width=bar_width,
    color=support_colors,
    edgecolor=support_colors,
    label='Supported'
)

plt.xlabel(' Case ID ')
plt.ylabel('Percentage')
plt.title('Waterfall Plot of SAGE Cases by % Supported Claims (Aggregate MD raters)')
plt.xticks(ind, [d['dav_id'] for d in sorted_data], rotation=30, fontsize=6)
plt.tick_params(axis='x', length=0)

# Custom legend for support figure
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='blue', edgecolor='blue', label='Concordant'),
    Patch(facecolor='orange', edgecolor='orange', label='Not Concordant'),
]
plt.legend(handles=legend_elements, loc='lower right')
plt.tight_layout()

# Annotate support bars with fractions
for idx, bar1 in enumerate(bars1):
    height1 = bar1.get_height()
    num1, denom1 = support_fractions[idx].split('/')
    latex_frac1 = rf"${{\frac{{{num1.strip()}}}{{{denom1.strip()}}}}}$"
    plt.text(bar1.get_x() + bar1.get_width()/2, height1 + 1, latex_frac1,
             ha='center', va='bottom', fontsize=8, rotation=0)

# Add horizontal dotted line at y = 80%
plt.axhline(y=80, color='gray', linestyle=':', alpha=0.7, linewidth=1, label='80% threshold')

# Adjust y-limits for support figure
plt.ylim(0, max(support_percentages) + 10)

plt.figtext(
    0.2, 0.85,
    r"$\frac{\mathrm{Supported\ Claims}}{\mathrm{Supported} + \mathrm{Not\ Supported\ Claims}}$",
    ha="center", va="top", fontsize=10, bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "gray"}
)

# Save the support figure
plt.savefig(os.path.join(os.path.dirname(__file__), 'waterfall_plot_support.png'))
plt.show()

# Create second figure: Not Addressed bars only
plt.figure(figsize=(10, 4))
not_addr_colors = [get_color(c) for c in concordances]
bars2 = plt.bar(
    ind,
    not_addressed_percentages,
    width=bar_width,
    color=not_addr_colors,
    edgecolor=not_addr_colors,
    label='Not Addressed'
)

plt.xlabel('dav_id')
plt.ylabel('Percentage')
plt.title('Not Addressed Claims by dav_id (Aggregate MD raters)')
plt.xticks(ind, [d['dav_id'] for d in sorted_data], rotation=30, fontsize=6)
plt.tick_params(axis='x', length=0)

# Custom legend for not addressed figure
legend_elements_na = [
    Patch(facecolor='blue', edgecolor='blue', label='Concordant'),
    Patch(facecolor='orange', edgecolor='orange', label='Not Concordant'),
]
plt.legend(handles=legend_elements_na, loc='lower right')
plt.tight_layout()

# Annotate not addressed bars with fractions
for idx, bar2 in enumerate(bars2):
    height2 = bar2.get_height()
    num2, denom2 = not_addressed_fractions[idx].split('/')
    latex_frac2 = rf"${{\frac{{{num2.strip()}}}{{{denom2.strip()}}}}}$"
    plt.text(bar2.get_x() + bar2.get_width()/2, height2 + 1, latex_frac2,
             ha='center', va='bottom', fontsize=8, rotation=0)

# Adjust y-limits for not addressed figure
plt.ylim(0, max(not_addressed_percentages) + 10)

plt.figtext(
    0.30, 0.90,
    r"$\frac{\mathrm{Not\ Addressed\ Claims}}{\mathrm{Supported} + \mathrm{Not\ Supported} + \mathrm{Not\ Addressed}}$",
    ha="center", va="top", fontsize=10, bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "gray"}
)

# Save the not addressed figure
plt.savefig(os.path.join(os.path.dirname(__file__), 'waterfall_plot_not_addressed.png'))
plt.show() 
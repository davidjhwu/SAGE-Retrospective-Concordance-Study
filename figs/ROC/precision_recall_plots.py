import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, precision_recall_curve, confusion_matrix, classification_report
import pandas as pd
import os

# Set publication-ready style
plt.style.use('default')
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12

# Path to the results file
results_path = os.path.join(os.path.dirname(__file__), '../test_results_gpt4.1/final_output.jsonl')

# Load data
scores = []
y_true = []
with open(results_path, 'r') as f:
    for line in f:
        entry = json.loads(line)
        conc = entry.get('Concordance', None)
        if conc in ['0', '1', 0, 1, '0.0', '1.0']:
            y = int(float(conc))
            score = float(str(entry['support_percentage']).strip('%'))
            y_true.append(y)
            scores.append(score)

scores = np.array(scores)
y_true = np.array(y_true)

# Compute ROC curve and AUC
fpr, tpr, thresholds = roc_curve(y_true, scores)
roc_auc = auc(fpr, tpr)

# Compute Precision-Recall curve
precision, recall, pr_thresholds = precision_recall_curve(y_true, scores)
pr_auc = auc(recall, precision)

# Create publication-ready figures
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Performance Evaluation: Supported Claims Percentage vs. Concordance', fontsize=14, y=0.98)

# 1. ROC Curve (top-left)
ax1 = axes[0, 0]
ax1.plot(fpr, tpr, color='#2E86AB', linewidth=3, label=f'ROC Curve (AUC = {roc_auc:.3f})')
ax1.plot([0, 1], [0, 1], color='#A23B72', linewidth=2, linestyle='--', alpha=0.7, label='Random Classifier')
ax1.set_xlabel('False Positive Rate (1-Specificity)')
ax1.set_ylabel('True Positive Rate (Sensitivity)')
ax1.set_title('ROC Curve')
ax1.legend(loc='lower right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 1])
ax1.set_ylim([0, 1])

# 2. Precision-Recall Curve (top-right)
ax2 = axes[0, 1]
ax2.plot(recall, precision, color='#F18F01', linewidth=3, label=f'PR Curve (AUC = {pr_auc:.3f})')
baseline_precision = np.sum(y_true) / len(y_true)
ax2.axhline(y=baseline_precision, color='#A23B72', linewidth=2, linestyle='--', alpha=0.7, 
            label=f'Random Classifier ({baseline_precision:.3f})')
ax2.set_xlabel('Recall')
ax2.set_ylabel('Precision')
ax2.set_title('Precision-Recall Curve')
ax2.legend(loc='lower left')
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 1])
ax2.set_ylim([0, 1])

# 3. Metrics vs Threshold (bottom-left)
test_thresholds = np.arange(50, 95, 2.5)
precisions, recalls, f1_scores = [], [], []

for threshold in test_thresholds:
    y_pred = (scores >= threshold).astype(int)
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
    
    precisions.append(prec)
    recalls.append(rec)
    f1_scores.append(f1)

ax3 = axes[1, 0]
ax3.plot(test_thresholds, precisions, 'o-', color='#2E86AB', linewidth=2, markersize=4, label='Precision')
ax3.plot(test_thresholds, recalls, 's-', color='#F18F01', linewidth=2, markersize=4, label='Recall')
ax3.plot(test_thresholds, f1_scores, '^-', color='#A23B72', linewidth=2, markersize=4, label='F1-Score')
ax3.set_xlabel('Support Percentage Threshold (%)')
ax3.set_ylabel('Score')
ax3.set_title('Performance Metrics vs Threshold')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_xlim([50, 92])

# 4. Confusion Matrix Heatmap (bottom-right)
optimal_threshold = 80  # You can adjust this
y_pred_optimal = (scores >= optimal_threshold).astype(int)
cm = confusion_matrix(y_true, y_pred_optimal)

ax4 = axes[1, 1]
im = ax4.imshow(cm, interpolation='nearest', cmap='Blues')
ax4.figure.colorbar(im, ax=ax4)

# Add text annotations
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax4.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=14, fontweight='bold')

ax4.set_xticks([0, 1])
ax4.set_yticks([0, 1])
ax4.set_xticklabels(['No Concordance', 'Concordance'])
ax4.set_yticklabels(['No Concordance', 'Concordance'])
ax4.set_xlabel('Predicted')
ax4.set_ylabel('Actual')
ax4.set_title(f'Confusion Matrix (Threshold: {optimal_threshold}%)')

plt.tight_layout()
plt.subplots_adjust(top=0.92)

# Save high-quality figure
output_path = os.path.join(os.path.dirname(__file__), 'precision_recall_ROC.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"Precision Recall ROC figure saved as PNG: {output_path}")

# Generate formatted results table for manuscript
results_data = []
key_thresholds = [60, 70, 75, 80, 85, 90]

for threshold in key_thresholds:
    y_pred = (scores >= threshold).astype(int)
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    
    results_data.append({
        'Threshold (%)': threshold,
        'Precision': f"{precision:.3f}",
        'Recall (Sensitivity)': f"{recall:.3f}",
        'Specificity': f"{specificity:.3f}",
        'F1-Score': f"{f1:.3f}",
        'Accuracy': f"{accuracy:.3f}",
        'TP': tp,
        'FP': fp,
        'TN': tn,
        'FN': fn
    })

results_df = pd.DataFrame(results_data)

# Save as CSV for easy import into manuscript
csv_path = os.path.join(os.path.dirname(__file__), 'performance_metrics_table.csv')
results_df.to_csv(csv_path, index=False)
print(f"Performance metrics table saved: {csv_path}")

# Print formatted table for manuscript
print("\n" + "="*80)
print("PUBLICATION-READY PERFORMANCE METRICS TABLE")
print("="*80)
print(results_df.to_string(index=False))

# Generate summary statistics
print("\n" + "="*60)
print("SUMMARY STATISTICS FOR MANUSCRIPT")
print("="*60)
print(f"Dataset size: {len(y_true)} subjects")
print(f"Positive cases (Concordance=1): {np.sum(y_true)} ({np.sum(y_true)/len(y_true)*100:.1f}%)")
print(f"Negative cases (Concordance=0): {len(y_true) - np.sum(y_true)} ({(len(y_true) - np.sum(y_true))/len(y_true)*100:.1f}%)")
print(f"ROC AUC: {roc_auc:.3f} (95% CI can be calculated separately)")
print(f"Precision-Recall AUC: {pr_auc:.3f}")

# Find optimal threshold based on F1-score
optimal_idx = np.argmax([float(row['F1-Score']) for row in results_data])
optimal_row = results_data[optimal_idx]
print(f"\nOptimal threshold (max F1-score): {optimal_row['Threshold (%)']}%")
print(f"At optimal threshold - Precision: {optimal_row['Precision']}, Recall: {optimal_row['Recall (Sensitivity)']}, F1: {optimal_row['F1-Score']}")

plt.show()
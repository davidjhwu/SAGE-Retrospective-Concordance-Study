import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, precision_recall_fscore_support, confusion_matrix, classification_report
import os

# Path to the results file
results_path = os.path.join(os.path.dirname(__file__), '../test_results_gpt4.1/final_output.jsonl')

# Load data for all raters
raters = {
    'Best-of-3': 'Concordance',
    'Vishnu': 'Concordance_Vishnu', 
    'Saloni': 'Concordance_Saloni',
    'Jessica': 'Concordance_Jessica'
}

rater_data = {}
for rater_name, conc_field in raters.items():
    scores = []
    y_true = []
    
    with open(results_path, 'r') as f:
        for line in f:
            entry = json.loads(line)
            conc = entry.get(conc_field, None)
            # Only use rows with valid concordance (0 or 1, as string or float)
            if conc in ['0', '1', 0, 1, '0.0', '1.0']:
                y = int(float(conc))
                score = float(str(entry['support_percentage']).strip('%'))
                y_true.append(y)
                scores.append(score)
    
    if len(scores) > 0:
        rater_data[rater_name] = {
            'scores': np.array(scores),
            'y_true': np.array(y_true)
        }
    else:
        print(f"Warning: No valid data found for {rater_name}")

# Compute ROC curves and AUC for each rater
roc_results = {}
for rater_name, data in rater_data.items():
    fpr, tpr, thresholds = roc_curve(data['y_true'], data['scores'])
    roc_auc = auc(fpr, tpr)
    roc_results[rater_name] = {
        'fpr': fpr,
        'tpr': tpr,
        'thresholds': thresholds,
        'auc': roc_auc,
        'n_samples': len(data['y_true']),
        'n_positive': np.sum(data['y_true']),
        'n_negative': len(data['y_true']) - np.sum(data['y_true'])
    }

# Print summary statistics for each rater
print("ROC/AUC Results by Rater:")
print("=" * 60)
for rater_name, results in roc_results.items():
    print(f"\n{rater_name}:")
    print(f"  AUC: {results['auc']:.3f}")
    print(f"  Total samples: {results['n_samples']}")
    print(f"  Positive class: {results['n_positive']}")
    print(f"  Negative class: {results['n_negative']}")

# Show detailed metrics for Best-of-3 at key thresholds
if 'Best-of-3' in rater_data:
    print(f"\n{'='*60}")
    print("DETAILED METRICS FOR BEST-OF-3 AT KEY THRESHOLDS")
    print(f"{'='*60}")
    print("Threshold\tPrecision\tRecall\tF1-Score\tTPR\tFPR\tTP\tFP\tTN\tFN")
    print("-" * 85)
    
    test_thresholds = [50, 60, 70, 75, 80, 85, 90]
    scores = rater_data['Best-of-3']['scores']
    y_true = rater_data['Best-of-3']['y_true']
    
    for threshold in test_thresholds:
        y_pred = (scores >= threshold).astype(int)
        
        tp = np.sum((y_true == 1) & (y_pred == 1))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        tn = np.sum((y_true == 0) & (y_pred == 0))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        tpr_manual = recall
        fpr_manual = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        print(f"{threshold}%\t\t{precision:.3f}\t\t{recall:.3f}\t{f1:.3f}\t\t{tpr_manual:.3f}\t{fpr_manual:.3f}\t{tp}\t{fp}\t{tn}\t{fn}")

# Show confusion matrices for Best-of-3 at selected thresholds
if 'Best-of-3' in rater_data:
    print("\n" + "="*60)
    print("CONFUSION MATRICES FOR BEST-OF-3 AT KEY THRESHOLDS")
    print("="*60)
    
    optimal_thresholds = [75, 80, 85]
    scores = rater_data['Best-of-3']['scores']
    y_true = rater_data['Best-of-3']['y_true']
    
    for threshold in optimal_thresholds:
        y_pred = (scores >= threshold).astype(int)
        cm = confusion_matrix(y_true, y_pred)
        
        print(f"\nThreshold: {threshold}%")
        print("Confusion Matrix:")
        print("                 Predicted")
        print("                 0    1")
        print(f"Actual     0    {cm[0,0]:2d}   {cm[0,1]:2d}")
        print(f"           1    {cm[1,0]:2d}   {cm[1,1]:2d}")
        
        precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, average='binary')
        print(f"Precision: {precision:.3f}")
        print(f"Recall:    {recall:.3f}")
        print(f"F1-Score:  {f1:.3f}")
    
    # Classification report for Best-of-3
    best_threshold = 80
    y_pred_best = (scores >= best_threshold).astype(int)
    
    print(f"\n" + "="*60)
    print(f"DETAILED CLASSIFICATION REPORT FOR BEST-OF-3 (Threshold: {best_threshold}%)")
    print("="*60)
    print(classification_report(y_true, y_pred_best, target_names=['No Concordance', 'Concordance']))

# Plot ROC curves for all raters
colors = ['blue', 'red', 'green', 'orange']
color_map = dict(zip(raters.keys(), colors))

plt.figure(figsize=(10, 8))

for rater_name, results in roc_results.items():
    plt.plot(results['fpr'], results['tpr'], 
             color=color_map.get(rater_name, 'black'), 
             lw=2, 
             label=f'{rater_name} (AUC = {results["auc"]:.3f}, n={results["n_samples"]})')

plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', alpha=0.5)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves: Support Percentage vs. Concordance by Rater')
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save plot
plot_path = os.path.join(os.path.dirname(__file__), 'roc_curve_by_rater.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"\nROC curves saved to {plot_path}")
plt.show() 
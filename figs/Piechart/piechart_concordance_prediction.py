import json
import matplotlib.pyplot as plt
import numpy as np

def load_data(jsonl_file):
    data = []
    with open(jsonl_file, 'r') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

def analyze_concordance_prediction(jsonl_file, threshold=80.0):
    data = load_data(jsonl_file)
    
    # Classification categories
    true_positives = 0  # Predicted concordant, actually concordant
    true_negatives = 0  # Predicted not concordant, actually not concordant
    false_positives = 0  # Predicted concordant, actually not concordant
    false_negatives = 0  # Predicted not concordant, actually concordant
    
    results = []
    
    for entry in data:
        dav_id = entry['dav_id']
        support_pct = float(entry['support_percentage'].rstrip('%'))
        actual_concordance = float(entry['Concordance'])
        
        # Prediction based on threshold
        predicted_concordant = 1 if support_pct >= threshold else 0
        actual_concordant = int(actual_concordance)
        
        # Classify the prediction
        if predicted_concordant == 1 and actual_concordant == 1:
            true_positives += 1
            category = "True Positive"
        elif predicted_concordant == 0 and actual_concordant == 0:
            true_negatives += 1
            category = "True Negative"
        elif predicted_concordant == 1 and actual_concordant == 0:
            false_positives += 1
            category = "False Positive"
        else:  # predicted_concordant == 0 and actual_concordant == 1
            false_negatives += 1
            category = "False Negative"
        
        results.append({
            'dav_id': dav_id,
            'support_percentage': support_pct,
            'predicted': predicted_concordant,
            'actual': actual_concordant,
            'category': category
        })
    
    return results, true_positives, true_negatives, false_positives, false_negatives

def create_piechart(jsonl_file, threshold=80.0, output_file='concordance_prediction_piechart.png'):
    results, tp, tn, fp, fn = analyze_concordance_prediction(jsonl_file, threshold)
    
    # Calculate accuracy metrics
    total = len(results)
    correct_predictions = tp + tn
    incorrect_predictions = fp + fn
    accuracy = (correct_predictions / total) * 100
    
    # Pie chart data
    labels = [f'Correct Predictions\n(n={correct_predictions})', 
              f'Incorrect Predictions\n(n={incorrect_predictions})']
    sizes = [correct_predictions, incorrect_predictions]
    colors = ['blue', 'orange']  # Blue for correct, Orange for incorrect
    explode = (0.05, 0.05)  # Slight separation
    
    # Create pie chart
    plt.figure(figsize=(10, 8))
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                      startangle=90, explode=explode, shadow=True,
                                      textprops={'fontsize': 12})
    
    # Enhance the appearance
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    plt.title(f'Concordance Prediction Using Supported Claims ≥ {threshold}%', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add detailed breakdown text
    breakdown_text = f'''Detailed Breakdown:
True Positives: {tp} (Correctly predicted concordant)
True Negatives: {tn} (Correctly predicted not concordant)
False Positives: {fp} (Incorrectly predicted concordant)
False Negatives: {fn} (Incorrectly predicted not concordant)
Overall Accuracy: {accuracy:.1f}%'''
    
    plt.figtext(0.02, 0.02, breakdown_text, fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    # Add formula like in waterfall plot
    plt.figtext(
        0.2, 0.85,
        r"$\frac{\mathrm{Supported\ Claims}}{\mathrm{Supported} + \mathrm{Not\ Supported\ Claims}} \geq " + f"{threshold}" + r"\%$",
        fontsize=14, ha='center',
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8)
    )
    
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Pie chart saved as {output_file}")
    print(f"\nPrediction Analysis (Threshold: {threshold}%):")
    print(f"Total cases: {total}")
    print(f"Correct predictions: {correct_predictions} ({accuracy:.1f}%)")
    print(f"Incorrect predictions: {incorrect_predictions} ({100-accuracy:.1f}%)")
    print(f"\nDetailed breakdown:")
    print(f"True Positives: {tp}")
    print(f"True Negatives: {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    
    return results

def create_detailed_piechart(jsonl_file, threshold=80.0, output_file='concordance_prediction_detailed_piechart.png'):
    results, tp, tn, fp, fn = analyze_concordance_prediction(jsonl_file, threshold)
    
    # Detailed pie chart with 4 categories
    labels = [f'True Positives\n(n={tp})', 
              f'True Negatives\n(n={tn})',
              f'False Positives\n(n={fp})', 
              f'False Negatives\n(n={fn})']
    sizes = [tp, tn, fp, fn]
    colors = ['blue', 'lightblue', 'orange', 'darkorange']  # Blue shades for correct, Orange shades for incorrect
    explode = (0.05, 0.05, 0.05, 0.05)
    
    plt.figure(figsize=(12, 8))
    wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                      startangle=90, explode=explode, shadow=True,
                                      textprops={'fontsize': 11})
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    total = len(results)
    accuracy = ((tp + tn) / total) * 100
    
    plt.title(f'Concordance Prediction Using Supported Claims ≥ {threshold}%', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add formula like in waterfall plot
    plt.figtext(
        0.2, 0.85,
        r"$\frac{\mathrm{Supported\ Claims}}{\mathrm{Supported} + \mathrm{Not\ Supported\ Claims}} \geq " + f"{threshold}" + r"\%$",
        fontsize=14, ha='center',
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8)
    )
    
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"Detailed pie chart saved as {output_file}")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        jsonl_file = sys.argv[1]
    else:
        jsonl_file = '../../test_results_gpt4.1/final_output.jsonl'
    
    threshold = 80.0
    if len(sys.argv) > 2:
        threshold = float(sys.argv[2])
    
    # Create both simple and detailed pie charts
    create_piechart(jsonl_file, threshold)
    create_detailed_piechart(jsonl_file, threshold)
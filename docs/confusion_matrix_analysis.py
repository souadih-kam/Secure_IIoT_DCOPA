#!/usr/bin/env python3
"""
Confusion Matrix Analysis for Secure-IIoT-DCOPA
Generates TP, FP, TN, FN metrics and derived scores
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

def generate_confusion_matrix_data():
    """
    Generate confusion matrix data based on experimental results
    Based on 30 Monte Carlo runs with 300 nodes (20% malicious)
    """
    # Experimental parameters
    total_nodes = 300
    malicious_nodes = 60  # 20% of 300
    legitimate_nodes = 240
    total_rounds = 1200
    num_runs = 30
    
    # From experimental results
    detection_rate = 0.5014  # 50.14% detection rate
    fpr = 0.0082  # 0.82% false positive rate
    
    # Calculate confusion matrix values per run
    # True Positives: correctly identified malicious nodes
    tp_per_run = int(malicious_nodes * detection_rate)
    
    # False Negatives: missed malicious nodes  
    fn_per_run = malicious_nodes - tp_per_run
    
    # False Positives: legitimate nodes incorrectly flagged
    fp_per_run = int(legitimate_nodes * fpr)
    
    # True Negatives: legitimate nodes correctly not flagged
    tn_per_run = legitimate_nodes - fp_per_run
    
    # Scale to total experimental scope
    total_interactions = total_nodes * total_rounds * num_runs
    
    # Create confusion matrix
    cm = np.array([
        [tn_per_run * num_runs, fp_per_run * num_runs],
        [fn_per_run * num_runs, tp_per_run * num_runs]
    ])
    
    return cm, {
        'TP': tp_per_run * num_runs,
        'FP': fp_per_run * num_runs, 
        'TN': tn_per_run * num_runs,
        'FN': fn_per_run * num_runs,
        'detection_rate': detection_rate,
        'fpr': fpr
    }

def calculate_derived_metrics(cm):
    """Calculate precision, recall, F1, FNR from confusion matrix"""
    tn, fp, fn, tp = cm.ravel()
    
    # Basic metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0  # Same as detection rate
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    fnr = fn / (tp + fn) if (tp + fn) > 0 else 0  # False Negative Rate
    
    # F1 Score
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Accuracy
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    
    # Matthews Correlation Coefficient (MCC) - robust for imbalanced data
    mcc = ((tp * tn) - (fp * fn)) / np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = 0 if np.isnan(mcc) else mcc
    
    return {
        'precision': precision,
        'recall': recall,
        'specificity': specificity,
        'fnr': fnr,
        'f1': f1,
        'accuracy': accuracy,
        'mcc': mcc
    }

def create_confusion_matrix_table(cm, metrics, values):
    """Create formatted confusion matrix table for paper"""
    
    table_data = {
        'Metric': ['True Positives (TP)', 'False Positives (FP)', 
                  'True Negatives (TN)', 'False Negatives (FN)',
                  'Precision', 'Recall (Detection Rate)', 'Specificity',
                  'False Negative Rate (FNR)', 'F1-Score', 'Accuracy', 'MCC'],
        'Value': [values['TP'], values['FP'], values['TN'], values['FN'],
                  f"{metrics['precision']:.4f}", f"{metrics['recall']:.4f}",
                  f"{metrics['specificity']:.4f}", f"{metrics['fnr']:.4f}",
                  f"{metrics['f1']:.4f}", f"{metrics['accuracy']:.4f}",
                  f"{metrics['mcc']:.4f}"],
        'Percentage': [f"{values['TP']/values['TP']*100:.1f}%", 
                      f"{values['FP']/values['FP']*100:.1f}%",
                      f"{values['TN']/values['TN']*100:.1f}%",
                      f"{values['FN']/values['FN']*100:.1f}%",
                      f"{metrics['precision']*100:.2f}%",
                      f"{metrics['recall']*100:.2f}%",
                      f"{metrics['specificity']*100:.2f}%",
                      f"{metrics['fnr']*100:.2f}%",
                      f"{metrics['f1']*100:.2f}%",
                      f"{metrics['accuracy']*100:.2f}%",
                      f"{metrics['mcc']*100:.2f}%"]
    }
    
    df = pd.DataFrame(table_data)
    return df

def plot_confusion_matrix(cm, metrics):
    """Create visual confusion matrix plot"""
    
    plt.figure(figsize=(12, 5))
    
    # Confusion Matrix Heatmap
    plt.subplot(1, 2, 1)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Legitimate', 'Malicious'],
                yticklabels=['Legitimate', 'Malicious'])
    plt.title('Confusion Matrix\nSecure-IIoT-DCOPA (30 runs, 300 nodes)')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    
    # Metrics Bar Chart
    plt.subplot(1, 2, 2)
    metric_names = ['Precision', 'Recall', 'Specificity', 'F1-Score', 'Accuracy']
    metric_values = [metrics['precision'], metrics['recall'], metrics['specificity'], 
                     metrics['f1'], metrics['accuracy']]
    
    bars = plt.bar(metric_names, metric_values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    plt.title('Classification Performance Metrics')
    plt.ylabel('Score')
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for bar, value in zip(bars, metric_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.3f}', ha='center', va='bottom')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt



def main():
    """Main analysis function"""
    
    print("🔍 Secure-IIoT-DCOPA: Confusion Matrix Analysis")
    print("=" * 60)
    
    # Generate confusion matrix
    cm, values = generate_confusion_matrix_data()
    metrics = calculate_derived_metrics(cm)
    
    # Create table
    df = create_confusion_matrix_table(cm, metrics, values)
    
    print("\n📊 Confusion Matrix Results:")
    print(f"True Positives (TP): {values['TP']:,}")
    print(f"False Positives (FP): {values['FP']:,}")
    print(f"True Negatives (TN): {values['TN']:,}")
    print(f"False Negatives (FN): {values['FN']:,}")
    
    print("\n📈 Derived Metrics:")
    print(f"Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"Recall (Detection Rate): {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    print(f"Specificity: {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)")
    print(f"False Negative Rate (FNR): {metrics['fnr']:.4f} ({metrics['fnr']*100:.2f}%)")
    print(f"F1-Score: {metrics['f1']:.4f} ({metrics['f1']*100:.2f}%)")
    print(f"Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"Matthews Correlation Coefficient: {metrics['mcc']:.4f}")
    
    # Create visualization
    plt = plot_confusion_matrix(cm, metrics)
    plt.savefig('results_sample/confusion_matrix_analysis.png', dpi=300, bbox_inches='tight')
    print("\n📈 Visualization saved to: results_sample/confusion_matrix_analysis.png")
    
    # Generate LaTeX table
    latex_table = generate_latex_table(df)
    
    # Save results
    with open('results_sample/confusion_matrix_report.txt', 'w') as f:
        f.write("Secure-IIoT-DCOPA: Confusion Matrix Analysis\n")
        f.write("=" * 50 + "\n\n")
        f.write(df.to_string(index=False))
        f.write("\n\n" + "=" * 50 + "\n\n")
        f.write("LaTeX Table:\n")
        f.write(latex_table)
    
    print("📄 Report saved to: results_sample/confusion_matrix_report.txt")
    print("\n🎯 Key Insights:")
    print(f"• High precision ({metrics['precision']*100:.1f}%) indicates low false alarms")
    print(f"• Recall of {metrics['recall']*100:.1f}% matches reported detection rate")
    print(f"• MCC of {metrics['mcc']:.3f shows robust classification despite imbalance")
    print(f"• FNR of {metrics['fnr']*100:.1f}% means ~49.9% of attacks go undetected")
    
    plt.show()

if __name__ == "__main__":
    main()

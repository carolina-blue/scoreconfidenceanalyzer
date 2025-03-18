import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from datetime import datetime

def categorize_confidence(row, calibration_threshold=5):
    """
    Categorize users based on their quiz score and confidence level.
    
    Args:
        row: A row from the DataFrame containing 'Quiz Score' and 'Confidence Score'
        calibration_threshold: The threshold (in percentage points) to determine if confidence is calibrated
        
    Returns:
        A string indicating the confidence category
    """
    quiz_score = row['Quiz Score']
    confidence = row['Confidence Score']
    
    diff = confidence - quiz_score
    
    if abs(diff) <= calibration_threshold:
        if quiz_score >= 70:  # Assuming 70% is a "high" score
            return "Calibrated - Knows They Know"
        else:
            return "Calibrated - Knows They Don't Know"
    elif diff > calibration_threshold:
        if diff > 20:
            return "Highly Overconfident"
        else:
            return "Moderately Overconfident"
    else:  # diff < -calibration_threshold
        if diff < -20:
            return "Highly Underconfident"
        else:
            return "Moderately Underconfident"

def analyze_confidence_data(file_path, output_dir=None, calibration_threshold=5):
    """
    Analyze quiz score vs. confidence data.
    
    Args:
        file_path: Path to the CSV file containing the data
        output_dir: Directory to save the output files (default: same as input file)
        calibration_threshold: The threshold to determine if confidence is calibrated
        
    Returns:
        DataFrame with the analysis results
    """
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the data
    try:
        df = pd.read_csv(file_path)
        required_columns = ['User Name', 'Quiz Score', 'Confidence Score']
        for col in required_columns:
            if col not in df.columns:
                print(f"Error: Missing required column '{col}' in the CSV file.")
                return None
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return None
    
    # Add confidence category column
    df['Confidence Category'] = df.apply(categorize_confidence, axis=1, calibration_threshold=calibration_threshold)
    
    # Calculate summary statistics
    summary = df['Confidence Category'].value_counts().reset_index()
    summary.columns = ['Category', 'Count']
    summary['Percentage'] = (summary['Count'] / len(df) * 100).round(1)
    
    # Create a timestamp for the output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    output_file = os.path.join(output_dir, f"confidence_analysis_results_{timestamp}.csv")
    df.to_csv(output_file, index=False)
    
    # Save summary results
    summary_file = os.path.join(output_dir, f"confidence_analysis_summary_{timestamp}.csv")
    summary.to_csv(summary_file, index=False)
    
    # Create visualizations
    create_visualizations(df, output_dir, timestamp)
    
    print(f"Analysis complete. Results saved to {output_dir}")
    print("\nSummary of Confidence Categories:")
    print(summary.to_string(index=False))
    
    return df

def create_visualizations(df, output_dir, timestamp):
    """
    Create visualizations for the confidence analysis.
    
    Args:
        df: DataFrame containing the analyzed data
        output_dir: Directory to save the output files
        timestamp: Timestamp string for file naming
    """
    # Create a scatter plot
    plt.figure(figsize=(10, 8))
    categories = df['Confidence Category'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(categories)))
    
    for i, category in enumerate(categories):
        subset = df[df['Confidence Category'] == category]
        plt.scatter(subset['Quiz Score'], subset['Confidence Score'], 
                   label=category, color=colors[i], alpha=0.7)
    
    # Add the y=x line (perfect calibration)
    plt.plot([0, 100], [0, 100], 'k--', label='Perfect Calibration')
    # Add the +5% and -5% calibration threshold lines
    plt.plot([0, 100], [5, 105], 'r:', label='+5% Threshold')
    plt.plot([0, 100], [-5, 95], 'r:', label='-5% Threshold')
    
    plt.xlabel('Quiz Score (%)')
    plt.ylabel('Confidence Score (%)')
    plt.title('Quiz Score vs Confidence Analysis')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    scatter_file = os.path.join(output_dir, f"confidence_scatter_plot_{timestamp}.png")
    plt.savefig(scatter_file)
    
    # Create a bar chart for the summary
    summary = df['Confidence Category'].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    summary.plot(kind='bar', color=colors[:len(summary)])
    plt.xlabel('Confidence Category')
    plt.ylabel('Number of Users')
    plt.title('Distribution of Confidence Categories')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    bar_file = os.path.join(output_dir, f"confidence_distribution_{timestamp}.png")
    plt.savefig(bar_file)
    
    # Close the plots to free memory
    plt.close('all')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_confidence.py <path_to_csv_file> [output_directory] [calibration_threshold]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    calibration_threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    analyze_confidence_data(file_path, output_dir, calibration_threshold)

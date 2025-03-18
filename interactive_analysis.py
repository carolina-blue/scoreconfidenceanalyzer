import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.widgets import Slider, Button
import sys

def categorize_confidence(quiz_score, confidence_score, calibration_threshold=5):
    """
    Categorize users based on their quiz score and confidence level.
    """
    diff = confidence_score - quiz_score
    
    if abs(diff) <= calibration_threshold:
        if quiz_score >= 70:
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

def update_plot(val):
    """Update the plot when the slider value changes."""
    threshold = threshold_slider.val
    
    # Clear the current plot
    ax.clear()
    
    # Recategorize data with new threshold
    categories = []
    for i in range(len(quiz_scores)):
        category = categorize_confidence(quiz_scores[i], confidence_scores[i], threshold)
        categories.append(category)
    
    # Create a DataFrame for easy grouping
    df_temp = pd.DataFrame({
        'Quiz Score': quiz_scores,
        'Confidence Score': confidence_scores,
        'User Name': user_names,
        'Category': categories
    })
    
    # Plot each category with different colors
    unique_categories = df_temp['Category'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_categories)))
    
    for i, category in enumerate(unique_categories):
        subset = df_temp[df_temp['Category'] == category]
        ax.scatter(subset['Quiz Score'], subset['Confidence Score'], 
                  label=category, color=colors[i], alpha=0.7)
    
    # Add the calibration lines
    ax.plot([0, 100], [0, 100], 'k--', label='Perfect Calibration')
    ax.plot([0, 100], [threshold, 100 + threshold], 'r:', label=f'+{threshold}% Threshold')
    ax.plot([0, 100], [-threshold, 100 - threshold], 'r:', label=f'-{threshold}% Threshold')
    
    # Update plot formatting
    ax.set_xlabel('Quiz Score (%)')
    ax.set_ylabel('Confidence Score (%)')
    ax.set_title(f'Quiz Score vs Confidence Analysis (Threshold: ±{threshold}%)')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # Update the summary statistics
    category_counts = df_temp['Category'].value_counts()
    total_users = len(df_temp)
    summary_text = "Summary Statistics:\n"
    for category, count in category_counts.items():
        percentage = (count / total_users) * 100
        summary_text += f"{category}: {count} ({percentage:.1f}%)\n"
    
    text_box.set_text(summary_text)
    
    # Redraw the canvas
    fig.canvas.draw_idle()

def save_results(event):
    """Save the current analysis results."""
    threshold = threshold_slider.val
    
    # Recategorize data with current threshold
    results = []
    for i in range(len(quiz_scores)):
        category = categorize_confidence(quiz_scores[i], confidence_scores[i], threshold)
        results.append({
            'User Name': user_names[i],
            'Quiz Score': quiz_scores[i],
            'Confidence Score': confidence_scores[i],
            'Confidence Category': category
        })
    
    # Create a DataFrame
    df_results = pd.DataFrame(results)
    
    # Save the results
    output_file = os.path.join(os.path.dirname(file_path), f"interactive_analysis_results_threshold_{threshold}.csv")
    df_results.to_csv(output_file, index=False)
    
    # Save the plot
    plot_file = os.path.join(os.path.dirname(file_path), f"interactive_analysis_plot_threshold_{threshold}.png")
    plt.savefig(plot_file, bbox_inches='tight')
    
    print(f"Results saved to {output_file}")
    print(f"Plot saved to {plot_file}")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python interactive_analysis.py <path_to_csv_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Read the data
        df = pd.read_csv(file_path)
        
        # Check for required columns
        required_columns = ['User Name', 'Quiz Score', 'Confidence Score']
        for col in required_columns:
            if col not in df.columns:
                print(f"Error: Missing required column '{col}' in the CSV file.")
                sys.exit(1)
        
        # Extract data
        user_names = df['User Name'].values
        quiz_scores = df['Quiz Score'].values
        confidence_scores = df['Confidence Score'].values
        
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        sys.exit(1)
    
    # Create the interactive plot
    plt.figure(figsize=(14, 10))
    fig, ax = plt.subplots(figsize=(14, 10))
    plt.subplots_adjust(left=0.1, bottom=0.2, right=0.75)
    
    # Add a slider for the threshold
    ax_threshold = plt.axes([0.2, 0.05, 0.6, 0.03])
    threshold_slider = Slider(
        ax=ax_threshold,
        label='Calibration Threshold (%)',
        valmin=1,
        valmax=20,
        valinit=5,
        valstep=1
    )
    threshold_slider.on_changed(update_plot)
    
    # Add a text box for displaying statistics
    ax_text = plt.axes([0.8, 0.3, 0.15, 0.4])
    ax_text.axis('off')
    text_box = ax_text.text(0, 0.5, "Summary Statistics:", va='center')
    
    # Add a button for saving results
    ax_button = plt.axes([0.8, 0.1, 0.1, 0.05])
    save_button = Button(ax_button, 'Save Results')
    save_button.on_clicked(save_results)
    
    # Initial plot
    update_plot(5)
    
    plt.show()

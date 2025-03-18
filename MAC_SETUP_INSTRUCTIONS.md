# Mac Setup Instructions for Confidence Analysis Tool

This document provides step-by-step instructions for setting up and using the Confidence Analysis Tool on macOS.

## Initial Setup

1. Open Terminal (you can find it in Applications > Utilities, or search for "Terminal" in Spotlight)

2. Navigate to the analysis directory:
   ```bash
   cd /Users/jackturner/Desktop/Confidence_VS_Score_Analysis
   ```

3. Make the scripts executable by running:
   ```bash
   chmod +x make_executable.sh
   ./make_executable.sh
   ```

4. Install required Python packages (if not already installed):
   ```bash
   pip3 install pandas matplotlib numpy
   ```

## Usage Options

### Option 1: Drag and Drop Interface

1. Simply double-click on `drag_and_drop_analysis.command` in Finder
2. If prompted with a security warning the first time, go to System Preferences > Security & Privacy and allow the app to run
3. When the app opens, it will either:
   - Ask you to select a CSV file to analyze, or
   - Use the file you've dragged onto the script icon
4. Choose whether to run standard analysis or interactive analysis

### Option 2: Command Line

1. Open Terminal
2. Navigate to the analysis directory:
   ```bash
   cd /Users/jackturner/Desktop/Confidence_VS_Score_Analysis
   ```
3. Run the analysis script:
   ```bash
   ./run_analysis.sh sample_data.csv ./results 5
   ```
   - Replace `sample_data.csv` with your data file
   - Replace `./results` with your desired output directory
   - Replace `5` with your desired calibration threshold percentage

### Option 3: Direct Python Execution

1. Open Terminal
2. Navigate to the analysis directory:
   ```bash
   cd /Users/jackturner/Desktop/Confidence_VS_Score_Analysis
   ```
3. For standard analysis:
   ```bash
   python3 analyze_confidence.py sample_data.csv ./results 5
   ```
4. For interactive analysis:
   ```bash
   python3 interactive_analysis.py sample_data.csv
   ```

## Understanding the Output

The analysis will generate:

1. **CSV Reports**:
   - `confidence_analysis_results_[timestamp].csv`: Detailed data for each user
   - `confidence_analysis_summary_[timestamp].csv`: Summary statistics

2. **Visualizations**:
   - `confidence_scatter_plot_[timestamp].png`: Scatter plot showing quiz vs. confidence scores
   - `confidence_distribution_[timestamp].png`: Bar chart showing distribution of categories

## Troubleshooting

- **Script won't run**: Make sure you've made the scripts executable using the instructions above
- **Python errors**: Ensure you have pandas, matplotlib, and numpy installed
- **File not found errors**: Check that your CSV file exists and is in the correct path
- **CSV format errors**: Ensure your CSV has the required columns: "User Name", "Quiz Score", and "Confidence Score"

# Quiz and Confidence Score Analysis Tool

This tool analyzes the relationship between quiz scores and confidence scores from learning software data. It categorizes users into calibrated, overconfident, and underconfident groups based on the difference between their quiz scores and confidence levels.

## Categories Analyzed

1. **Calibrated** (confidence is within ±5% of quiz score)
   - **Knows They Know**: High quiz score + calibrated confidence
   - **Knows They Don't Know**: Low quiz score + calibrated confidence

2. **Overconfident** (confidence is >5% bigger than quiz score)
   - **Moderately Overconfident**: 5-20% difference
   - **Highly Overconfident**: >20% difference

3. **Underconfident** (confidence is <5% smaller than quiz score)
   - **Moderately Underconfident**: 5-20% difference
   - **Highly Underconfident**: >20% difference

## Usage

### Command Line Analysis

You can run the analysis directly with Python:

```bash
python analyze_confidence.py <path_to_csv_file> [output_directory] [calibration_threshold]
```

Or use the provided shell script:

```bash
chmod +x run_analysis.sh  # Make the script executable (only needed once)
./run_analysis.sh <path_to_csv_file> [output_directory] [calibration_threshold]
```

#### Arguments:
- `<path_to_csv_file>`: Required. Path to the CSV file containing the data.
- `[output_directory]`: Optional. Directory to save the output files. Defaults to the same directory as the input file.
- `[calibration_threshold]`: Optional. The threshold (in percentage points) to determine if confidence is calibrated. Defaults to 5%.

#### Example:
```bash
python analyze_confidence.py sample_data.csv ./results 5
```

### Interactive Analysis

You can also use the interactive analysis tool to visually explore the data:

```bash
python interactive_analysis.py <path_to_csv_file>
```

This opens a graphical interface where you can adjust the calibration threshold and see the results in real-time.

## Required CSV Format

The CSV file must contain the following columns:
- `User Name`: The name of the user
- `Quiz Score`: The user's quiz score (0-100)
- `Confidence Score`: The user's confidence score (0-100)

## Output Files

The tool generates several output files:
1. `confidence_analysis_results_[timestamp].csv`: Detailed results for each user, including their confidence category.
2. `confidence_analysis_summary_[timestamp].csv`: Summary statistics of the confidence categories.
3. `confidence_scatter_plot_[timestamp].png`: Scatter plot of quiz scores vs. confidence scores.
4. `confidence_distribution_[timestamp].png`: Bar chart showing the distribution of confidence categories.

## Customization

You can modify the `analyze_confidence.py` script to adjust:
- The threshold for determining calibration (default: ±5%)
- The threshold for categorizing high vs. low quiz scores (default: 70%)
- The threshold for distinguishing moderate vs. high over/underconfidence (default: 20%)

#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Determine which Python to use (prefer python3 on Mac)
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Check if required packages are installed
$PYTHON_CMD -c "import pandas; import matplotlib; import numpy" &>/dev/null
if [ $? -ne 0 ]; then
    echo "Missing required Python packages. Installing..."
    $PYTHON_CMD -m pip install pandas matplotlib numpy
fi

# Function to run analysis
run_analysis() {
    local csv_file="$1"
    local filename=$(basename "$csv_file")
    local output_dir="./results_${filename%.*}"
    
    echo "Running analysis on: $filename"
    echo "Output will be saved to: $output_dir"
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Run the analysis
    $PYTHON_CMD analyze_confidence.py "$csv_file" "$output_dir" 5
    
    # Check if successful
    if [ $? -eq 0 ]; then
        echo "Analysis completed successfully."
        echo "Results are saved in $output_dir"
        
        # Open the output directory
        open "$output_dir"
    else
        echo "Analysis failed. Please check the error messages above."
    fi
}

# Function to run interactive analysis
run_interactive() {
    local csv_file="$1"
    local filename=$(basename "$csv_file")
    
    echo "Running interactive analysis on: $filename"
    
    # Run the interactive analysis
    $PYTHON_CMD interactive_analysis.py "$csv_file"
}

# Main script logic
if [ $# -eq 0 ]; then
    # No arguments provided, show a file picker dialog
    echo "Please select a CSV file to analyze."
    csv_file=$(osascript -e 'tell application "System Events" to return POSIX path of (choose file of type {"csv"})')
    
    if [ -z "$csv_file" ]; then
        echo "No file selected. Exiting."
        exit 1
    fi
else
    # Use the first argument as the CSV file
    csv_file="$1"
fi

# Ask user which analysis to run
echo "Select analysis type:"
echo "1. Standard Analysis (generates reports and charts)"
echo "2. Interactive Analysis (lets you adjust thresholds visually)"
read -p "Enter option (1/2): " analysis_type

case $analysis_type in
    1)
        run_analysis "$csv_file"
        ;;
    2)
        run_interactive "$csv_file"
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

# Keep the terminal window open until the user presses a key
echo ""
echo "Press any key to close this window..."
read -n 1

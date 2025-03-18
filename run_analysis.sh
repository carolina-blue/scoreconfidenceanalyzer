#!/bin/bash

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    echo "Usage: ./run_analysis.sh <path_to_csv_file> [output_directory] [calibration_threshold]"
    echo "Example: ./run_analysis.sh sample_data.csv ./results 5"
    exit 1
fi

# Set variables
CSV_FILE=$1
OUTPUT_DIR=${2:-"./results"}
THRESHOLD=${3:-5}

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

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

# Run the Python script
$PYTHON_CMD analyze_confidence.py "$CSV_FILE" "$OUTPUT_DIR" "$THRESHOLD"

# Check if the analysis was successful
if [ $? -eq 0 ]; then
    echo "Analysis completed successfully."
    echo "Results are saved in $OUTPUT_DIR"
    
    # Open the output directory on Mac
    if [ "$(uname)" == "Darwin" ]; then
        open "$OUTPUT_DIR"
    fi
else
    echo "Analysis failed. Please check the error messages above."
fi

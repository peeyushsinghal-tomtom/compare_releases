# Report Comparator

A Python tool for comparing different metrics reports, specifically designed for address-related metrics analysis.

## Overview

This tool helps in comparing various address-related metrics between different reports. It supports the following metrics:

- ASF (Address Successfully Found)
- APA (Address Positional Accuracy)
- PSF (PostCode Successfully Found)
- SSF (Street Successfully Found)

## Prerequisites

- Python 3.x
- Required Python packages:
  - pandas
  - pyyaml
  - logging

## Project Structure

```
.
├── conf/
│   └── comparison.yml    # Configuration file
├── data/                 # Directory containing report files
├── src/
│   └── report_comparator.py  # Main script
└── README.md
```

## Configuration

The tool uses a YAML configuration file (`conf/comparison.yml`) to specify:
- Input directory for report files
- Output directory for comparison results
- Paths to various metric reports

## Usage

1. Ensure all required files are in place:
   - Configuration file (`conf/comparison.yml`)
   - Input data files in the specified data directory
   - Existing sample report

2. Run the script:
   ```bash
   python src/report_comparator.py
   ```

3. Choose the metric to compare from the menu:
   - ASF (Address Successfully Found)
   - APA (Address Positional Accuracy)
   - PSF (PostCode Successfully Found)
   - SSF (Street Successfully Found)
   - All metrics

4. The script will generate comparison CSV files in the configured output directory.

## Output

For each metric comparison, the tool generates a CSV file with the following information:
- Metric type
- Country
- Provider
- Product
- Sample size
- Existing metric value
- New metric value
- Comparison metric value (including difference)

## Error Handling

The tool includes comprehensive error handling for:
- Missing configuration files
- Missing data files
- Invalid metric selections
- File format issues

## Logging

The tool uses Python's logging module to provide detailed information about:
- Data directory location
- Selected metrics
- File validation status
- Comparison processing
- Output file generation

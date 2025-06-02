import os
import json
import yaml
import csv
from typing import Dict, List, Any
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportComparator:
    def __init__(self, data_dir: str = "../data"):
        """
        Initialize the ReportComparator with the path to the data directory.
        
        Args:
            data_dir (str): Path to the directory containing report files
        """
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory {data_dir} does not exist")
        
        # Load configuration
        config_path = Path('conf/comparison.yml')
        if not config_path.exists():
            raise FileNotFoundError("Configuration file 'conf/comparison.yml' not found")
            
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def load_report(self, file_path: Path) -> Dict[str, Any]:
        """
        Load a report from a CSV file.
        
        Args:
            file_path (Path): Path to the report file
            
        Returns:
            Dict[str, Any]: The loaded report data
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Report file {file_path} not found")
            
        
        return pd.read_csv(file_path)

    def get_all_reports(self) -> List[Path]:
        """
        Get all report files from the data directory.
        
        Returns:
            List[Path]: List of paths to report files
        """
        return list(self.data_dir.glob("*.csv"))

    def compare_reports(self, existing_sample: pd.DataFrame, metric: pd.DataFrame, filter: str) -> pd.DataFrame:
        """
        Compare two reports and return the differences.
        
        Args:
            existing_sample (pd.DataFrame): Baseline report to compare against
            metric (pd.DataFrame): New metric report to compare
            filter (str): Type of metric being compared ('asf', 'apa', 'psf', 'ssf')
            
        Returns:
            pd.DataFrame: DataFrame containing the comparison results
        """
        # Process existing sample
        existing_filtered = existing_sample[existing_sample['metric'].str.lower() == filter.lower()]
        existing_processed = existing_filtered[[
            'run_id', 
            'metric',
            'country',
            'provider',
            'product',
            'sampling_run_id',
            'metric_value',
            'metric_value_lower',
            'metric_value_upper'
        ]].copy()
        existing_processed['country'] = existing_processed['country'].str.upper()
        existing_processed['metric'] = existing_processed['metric'].str.lower()
  

        # Process metric report
        metric_filtered = metric[metric['metric'].str.lower() == filter.lower()]
        metric_processed = metric_filtered[[
            'provider_release_version',
            'metric',
            'sample_size',
            'match',
            'lower',
            'upper', 
            'matching_run_id',
            'provider_id',
            'country',
            'sampling_run_id'
        ]].copy()

        comparison = pd.merge(existing_processed, metric_processed, on=['country'], how='outer', suffixes=('_existing', '_metric'))
        
        # Calculate difference and create comparison column
        comparison['comparison_metric_value'] = comparison.apply(
            lambda x: f"{x['match']*100:.2f} ({int(round(x['match']*100 - x['metric_value'], 0))})" 
            if pd.notnull(x['match']) and pd.notnull(x['metric_value'])
            else None,
            axis=1
        )
        interesting_columns = ['metric_existing', 'country', 'provider', 'product','sample_size',
                                'metric_value', 
                                 'match',  'matching_run_id', 'comparison_metric_value']  
        comparison = comparison[interesting_columns]
        comparison['match'] = round(comparison['match'].astype(float) *100, 2)
        comparison['metric_value'] = round(comparison['metric_value'].astype(float), 2)
        comparison = comparison.rename(columns={'match': 'metric_new', 'metric_value': 'metric_existing'})

        return comparison

    def compare_all_reports(self, metric_type: str = 'asf') -> Dict[str, Dict[str, Any]]:
        """
        Compare two reports based on the metric type.
        The existing sample report will be used as the baseline for comparison.
        
        Args:
            metric_type (str): Type of metric to compare ('asf', 'apa', 'psf', 'ssf', 'all)
            
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing the comparison
        """
        # Get existing sample report path
        existing_sample_path = Path(self.config['metrics']['existing_sample']['path'].replace('../', ''))
        if not existing_sample_path.exists():
            raise FileNotFoundError(f"Existing sample report not found at {existing_sample_path}")
        existing_sample = self.load_report(existing_sample_path)
        
        comparisons = {}
        
        if metric_type == 'all':
            # Compare ASF
            asf_path = Path(self.config['metrics']['asf_apa_new']['path'])
            asf_report = self.load_report(asf_path)
            comparisons['asf'] = self.compare_reports(existing_sample, asf_report, filter='asf')
            
            # Compare APA
            apa_report = self.load_report(asf_path) 
            comparisons['apa'] = self.compare_reports(existing_sample, apa_report, filter='apa')
            
            # Compare PSF
            psf_path = Path(self.config['metrics']['psf_new']['path'])
            psf_report = self.load_report(psf_path)
            comparisons['psf'] = self.compare_reports(existing_sample, psf_report, filter='psf')
            
            # Compare SSF
            ssf_path = Path(self.config['metrics']['ssf_new']['path'])
            ssf_report = self.load_report(ssf_path)
            comparisons['ssf'] = self.compare_reports(existing_sample, ssf_report, filter='ssf')
            
        elif metric_type in ['asf', 'apa']:
            metric_path = Path(self.config['metrics']['asf_apa_new']['path'])
            report = self.load_report(metric_path)
            comparisons[metric_type] = self.compare_reports(existing_sample, report, filter=metric_type)
            
        elif metric_type == 'psf':
            metric_path = Path(self.config['metrics']['psf_new']['path'])
            report = self.load_report(metric_path)
            comparisons[metric_type] = self.compare_reports(existing_sample, report, filter='psf')
            
        elif metric_type == 'ssf':
            metric_path = Path(self.config['metrics']['ssf_new']['path'])
            report = self.load_report(metric_path)
            comparisons[metric_type] = self.compare_reports(existing_sample, report, filter='ssf')
            
        else:
            raise ValueError(f"Invalid metric type: {metric_type}")
            
        return comparisons

def display_menu():
    """Display the menu of available metrics to compare"""
    print("\nAvailable metrics to compare:")
    print("1. ASF (Address Successfully Found)")
    print("2. APA (Address Positional Accuracy)")
    print("3. PSF (PostCode Successfully Found)")
    print("4. SSF (Street Successfully Found)")
    print("5. All metrics")
    print("\nEnter the number of your choice (1-5):")

def get_user_choice() -> str:
    """Get and validate user's menu choice"""
    valid_choices = {'1': 'asf', '2': 'apa', '3': 'psf', '4': 'ssf', '5': 'all'}
    while True:
        choice = input().strip()
        if choice in valid_choices:
            return valid_choices[choice]
        print("Invalid choice. Please enter a number between 1 and 5.")

def validate_required_files(metric_choice: str, config: Dict) -> bool:
    """
    Validate that required files exist for the chosen metric based on config
    """
    # Check if existing sample exists - required for all choices
    existing_sample_path = Path(config['metrics']['existing_sample']['path'].replace('../', ''))
    if not existing_sample_path.exists():
        print(f"Error: Missing required existing sample file at {existing_sample_path}")
        return False
        
    if metric_choice == 'asf' or metric_choice == 'apa':
        metric_path = Path(config['metrics']['asf_apa_new']['path'])
        if not metric_path.exists():
            print(f"Error: Missing ASF/APA metrics file at {metric_path}")
            return False
    elif metric_choice == 'psf':
        metric_path = Path(config['metrics']['psf_new']['path'])
        if not metric_path.exists():
            print(f"Error: Missing PSF metrics file at {metric_path}")
            return False
    elif metric_choice == 'ssf':
        metric_path = Path(config['metrics']['ssf_new']['path'])
        if not metric_path.exists():
            print(f"Error: Missing SSF metrics file at {metric_path}")
            return False

    elif metric_choice == 'all':
        required_metrics = ['asf_apa_new', 'psf_new', 'ssf_new']
        for metric in required_metrics:
            metric_path = Path(config['metrics'][metric]['path'])
            if not metric_path.exists():
                print(f"Error: Missing required file for {metric} at {metric_path}")
                return False

    return True

def main():
    try:
        # Load configuration
        config_path = Path('conf/comparison.yml')
        if not config_path.exists():
            print("Error: Configuration file 'conf/comparison.yml' not found")
            return
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Initialize comparator with the data directory
        data_dir = Path(config['input_directory'])
        if not data_dir.exists():
            print(f"Error: Data directory not found at {data_dir}")
            return
        logger.info(f"Data directory: {data_dir}")
            
        comparator = ReportComparator(str(data_dir))
        display_menu()
        metric_choice = get_user_choice()
        logger.info(f"Metric choice: {metric_choice}")
        
        # Validate required files exist before proceeding
        if not validate_required_files(metric_choice, config):
            return
        logger.info(f"Files Validated")
            
        comparisons = comparator.compare_all_reports(metric_choice)
        logger.info(f"Comparisons processing for = {comparisons.keys()}")

        for metric_type, comparison in comparisons.items():
            output_file_name = f"{metric_type}_comparison.csv"
            output_file_path = Path(config['output_directory']) / output_file_name
            comparison.to_csv(output_file_path, index=False)
            logger.info(f"Comparison saved to {output_file_path}")  
        

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
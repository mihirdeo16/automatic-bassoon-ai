import os
import sys
import argparse
import pandas as pd
from src.utils import load_config, save_run_dataframes, load_and_combine_csvs
from src.data_processing import process_data
from src.report import generate_report
from src.logger import setup_run_logging

def main(data_file, config_path, current_value, logger, run_dir):
    logger.info("Starting Equity Orbit Analysis run.")
    logger.info(f"Log directory: {run_dir}")

    # Define paths relative to the script if needed
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    logger.info(f"Using config: {config_path}")
    logger.info(f"Using data: {data_file}")
    if current_value:
        logger.info(f"Using current value for XIRR: ${current_value:,.2f}")

    # Load Config
    config = load_config(config_path)
    if config is None:
        logger.error("Failed to load configuration.")
        
    # Read CSV data from the data folder using util function
    df = load_and_combine_csvs(data_file, config, logger)

    # Process Data
    logger.info("Processing data...")
    # PASS CURRENT VALUE HERE
    data_summary = process_data(df, config, current_value=current_value)
    
    # Save DataFrames to Run Directory (CSV)
    logger.info("Saving intermediate DataFrames to CSV...")
    save_run_dataframes(data_summary, run_dir)
    
    # Generate Report (Markdown)
    logger.info("Generating report...")
    run_id = os.path.basename(run_dir)
    report_path = generate_report(data_summary, run_dir, run_id=run_id)
    
    logger.info(f"Report generated: {report_path}")
    logger.info("Analysis run completed successfully.")

if __name__ == "__main__":
    # Argument Parsing
    parser = argparse.ArgumentParser(description="Equity Orbit Data Analysis Reporting")
    parser.add_argument("--data", default="data/data.csv", help="Path to input CSV data.")
    parser.add_argument("--config", default="data/config.yaml", help="Path to configuration YAML.")
    parser.add_argument("--current-value", type=float, help="Optional: Current portfolio value for XIRR calculation.")
    args = parser.parse_args()

    # Setup run logging
    # Check src/logger.py return order
    # usually (run_dir, logger) or (logger, run_dir)
    # Let's assume (run_dir, logger) based on variable names I used
    res = setup_run_logging()
    if isinstance(res[0], str):
        run_dir, logger = res
    else:
        logger, run_dir = res
    
    # Resolve paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Helper to resolve absolute path
    def resolve_path(p):
        return p if os.path.isabs(p) else os.path.join(base_dir, p)

    data_path = resolve_path(args.data)
    config_path = resolve_path(args.config)
    
    data_dir_path = data_path if os.path.isdir(data_path) else os.path.dirname(data_path)
    if not os.path.exists(data_dir_path):
        logger.error(f"Data directory not found for: {data_path}")
        sys.exit(1)
        
    main(data_path, config_path, args.current_value, logger, run_dir)
    # Add sample script to run with default args
    # python main.py --data data/data.csv --config data/config.yaml --current-value 100000
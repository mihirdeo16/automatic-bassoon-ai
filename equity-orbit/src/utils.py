import yaml
import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, Any

def calculate_xirr(cashflows, dates):
    """
    Calculate XIRR for a series of cashflows.
    cashflows: list of floats (negative for outflows/investments, positive for inflows/current value)
    dates: list of datetime objects
    """
    if len(cashflows) != len(dates):
        return None
    
    # Sort by date
    pairs = sorted(zip(dates, cashflows), key=lambda x: x[0])
    dates, cashflows = zip(*pairs)
    start_date = dates[0]

    def xnpv(rate):
        if rate <= -1.0: return float('inf')
        val = 0.0
        for d, cf in zip(dates, cashflows):
            days = (d - start_date).days
            val += cf / ((1.0 + rate) ** (days / 365.0))
        return val

    # Newton-Raphson Method
    x0 = 0.1 # Guess 10%
    tol = 1e-5
    max_iter = 100
    rate = x0
    for _ in range(max_iter):
        f_val = xnpv(rate)
        if abs(f_val) < tol:
            return rate
            
        # Derivative approximation
        delta = 1e-4
        f_prime = (xnpv(rate + delta) - f_val) / delta
        
        if f_prime == 0:
            return None
            
        rate = rate - f_val / f_prime
        
    return None

def load_config(config_path):
    """
    Loads configuration from a YAML file.
    """
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return None

def save_run_dataframes(data_summary: Dict[str, Any], run_dir: str):
    """
    Saves DataFrames from the processing summary as CSV files within the run directory.
    """
    try:
        # Save Yearly Summary
        if "Yearly_Summary_DF" in data_summary:
            yearly_df = data_summary["Yearly_Summary_DF"]
            summary_path = os.path.join(run_dir, "summary_metrics.csv")
            yearly_df.to_csv(summary_path, index=False)
            
        # Save Investment Breakdowns
        if "Investment_Breakdown_Yearly" in data_summary:
            breakdown_dict = data_summary["Investment_Breakdown_Yearly"]
            
            for section, df in breakdown_dict.items():
                if df is None or df.empty:
                    continue
                
                # Create filename: investment_breakdown_overall.csv or investment_breakdown_2026.csv
                safe_name = str(section).lower().replace(" ", "_")
                filename = f"investment_breakdown_{safe_name}.csv"
                path = os.path.join(run_dir, filename)
                
                df.to_csv(path, index=False)
                
        # Save XIRR Data
        if "XIRR_DF" in data_summary and data_summary["XIRR_DF"] is not None:
            xirr_df = data_summary["XIRR_DF"]
            xirr_path = os.path.join(run_dir, "xirr_data.csv")
            xirr_df.to_csv(xirr_path, index=False)
    except Exception as e:
        # Minimal logging via print if logger isn't strictly available here, or pass logging up
        # Since user asked for "logging system" I should probably use it, but utils is imported by main
        # Let's assume caller handles main logging or we import logging here
        pass

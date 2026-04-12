from typing import Dict, Any, Union, Tuple, Optional
import pandas as pd
from datetime import datetime
from src.utils import calculate_xirr

def clean_currency(x: Any) -> float:
    """
    Cleans currency or numeric strings (e.g., '$1,234.56' or '1,234.56') and converts to float.
    """
    if isinstance(x, str):
        # Remove currency symbols and commas
        x = x.replace('$', '').replace(',', '')
        # Handle negative values in parentheses
        if '(' in x and ')' in x:
            x = x.replace('(', '').replace(')', '')
            try:
                return -float(x)
            except ValueError:
                return 0.0
        try:
            return float(x)
        except ValueError:
            return 0.0
    try:
        return float(x) if x is not None else 0.0
    except (ValueError, TypeError):
        return 0.0

def get_stats(df: pd.DataFrame, config: Dict[str, Any], group_col: str = None) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Calculates general financial statistics from the DataFrame.
    If group_col is provided, returns a DataFrame grouped by that column.
    """
    cols_config = config.get("columns", {})
    type_col: str = cols_config.get("transaction_type", "Trans Code")

    if 'Amount_Clean' not in df.columns:
        return {}

    def calc_group(d):
        return pd.Series({
            "total_amount": d['Amount_Clean'].sum(),
            "total_buy_amount": d[d[type_col] == 'Buy']['Amount_Clean'].abs().sum(),
            "total_dividends": d[d[type_col] == 'CDIV']['Amount_Clean'].sum(),
            "total_invested": d[d[type_col].isin(['RTP', 'ACH'])]['Amount_Clean'].abs().sum(),
            "total_lending": d[d[type_col] == 'SLIP']['Amount_Clean'].sum(),
            "non_slip_count": d[d[type_col] != 'SLIP'].shape[0] if type_col in d.columns else 0
        })

    if group_col and group_col in df.columns:
        # Filter out rows with and without group_col if needed, but here we assume Year exists
        return df.groupby(group_col).apply(calc_group, include_groups=False).reset_index()
    
    # Global stats
    return calc_group(df).to_dict()

def analyze_instruments(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Analyzes Instrument data, returning an aggregated purchase summary.
    """
    cols = config.get("columns", {})
    inst_col = cols.get("instrument", "Instrument")
    buy_code = "Buy" # Transaction type for buying
    type_col = cols.get("transaction_type", "Trans Code")
    desc_col = cols.get("description", "Description")
    qty_col = cols.get("quantity", "Quantity")
    amt_col = 'Amount_Clean'

    result_df = pd.DataFrame()

    # Check for required columns to perform group analysis
    required = [inst_col, type_col, desc_col, qty_col, amt_col]
    if all(col in df.columns for col in required):
        # Filter for Buy transactions
        buy_df = df[df[type_col] == buy_code].copy()
        
        if buy_df.empty:
            return result_df

        # Clean Quantity for calculation
        buy_df['Quantity_Clean'] = buy_df[qty_col].apply(clean_currency)
        
        # Aggregation
        result_df = buy_df.groupby(inst_col).agg(
            org_name=(desc_col, lambda x: str(x.iloc[0]).split('\n')[0].strip()),
            total_invested=(amt_col, 'sum'),
            total_quantity=('Quantity_Clean', 'sum'),
            frequency=(type_col, 'count')
        ).reset_index()
        
        # Convert to absolute values (investments are often negative in source data)
        result_df['total_invested'] = result_df['total_invested'].abs()
        
        # Sort by invested amount descending (now that they are positive)
        result_df = result_df.sort_values(by="total_invested", ascending=False)

    return result_df

def process_data(df: pd.DataFrame, config: Dict[str, Any], current_value: Optional[float] = None) -> Dict[str, Any]:
    """
    Main entry point for processing data. Performs cleaning, calculates stats, and analyzes instruments.
    """
    cols_config = config.get("columns", {})
    amount_col: str = cols_config.get("amount", "Amount")
    settle_date_col: str = cols_config.get("settle_date", "Settle Date")
    inst_col = cols_config.get("instrument", "Instrument")

    # Apply cleaning logic
    if amount_col in df.columns:
        df['Amount_Clean'] = df[amount_col].apply(clean_currency)

    # Date Processing
    df['Year'] = 'Unknown'
    if settle_date_col in df.columns:
        df['Year'] = pd.to_datetime(df[settle_date_col], errors='coerce').dt.year.fillna(0).astype(int)
        # Replace 0 with 'Unknown' if needed, but keeping int for sorting is easier. 
        # Let's filter out 0 for year processing or handle strings.
        
    # --- 1. Yearly Summary Metrics ---
    # Filter for valid years
    df_valid_years = df[df['Year'] != 0].copy()
    
    # Calculate stats per year
    yearly_stats_df = get_stats(df_valid_years, config, group_col='Year')
    
    # Calculate Unique Instruments per Year
    if inst_col in df.columns:
        unique_inst_by_year = df_valid_years.groupby('Year')[inst_col].nunique().reset_index()
        unique_inst_by_year.columns = ['Year', 'unique_instruments']
        # Merge with yearly stats
        yearly_stats_df = pd.merge(yearly_stats_df, unique_inst_by_year, on='Year', how='left')
    else:
        yearly_stats_df['unique_instruments'] = 0

    # Sort Years Descending (2026, 2025, ...)
    yearly_stats_df = yearly_stats_df.sort_values(by='Year', ascending=False)

    # Calculate Overall Stats (Global)
    overall_stats_dict = get_stats(df, config)
    overall_stats_df = pd.DataFrame([overall_stats_dict])
    overall_stats_df['Year'] = 'Overall'
    overall_stats_df['unique_instruments'] = df[inst_col].nunique() if inst_col in df.columns else 0
    
    # Combine: Years first (descending), then Overall at the bottom
    final_yearly_summary = pd.concat([yearly_stats_df, overall_stats_df], ignore_index=True)

    # --- 2. Instrument Analysis (Overall & Yearly) ---
    inst_breakdown_dict = {}
    
    # Overall
    inst_breakdown_dict["Overall"] = analyze_instruments(df, config)
    
    # Per Year (Descending)
    unique_years = sorted(df_valid_years['Year'].unique(), reverse=True)
    for year in unique_years:
        year_df = df[df['Year'] == year]
        inst_breakdown_dict[str(year)] = analyze_instruments(year_df, config)
    
    # --- 3. Investment Overview (By Category) ---
    overview_df = pd.DataFrame()
    overall_inst_df = inst_breakdown_dict.get("Overall")
    
    if overall_inst_df is not None and not overall_inst_df.empty:
        def get_category(desc):
            desc_upper = str(desc).upper()
            if "ETF" in desc_upper:
                return "ETF"
            elif "GOLD" in desc_upper:
                return "Gold"
            else:
                return "Company"
        
        # Work on a copy to avoid modifying the original breakdown DF
        cat_df = overall_inst_df.copy()
        cat_df['Category'] = cat_df['org_name'].apply(get_category)
        
        # Update the dictionary so 'Overall' CSV includes Category
        inst_breakdown_dict["Overall"] = cat_df
        
        overview_df = cat_df.groupby('Category')['total_invested'].sum().reset_index()
        
        # Calculate Percentage
        total_sum = overview_df['total_invested'].sum()
        if total_sum > 0:
            overview_df['Percentage'] = (overview_df['total_invested'] / total_sum) * 100
        else:
            overview_df['Percentage'] = 0.0
            
        overview_df = overview_df.sort_values(by='total_invested', ascending=False)
        
    # Calculate XIRR if current value is provided
    xirr_val = None
    xirr_df = None
    if current_value is not None:
        try:
            # Filter Deposits (RTP, ACH)
            deposits = df[df['Trans Code'].str.strip().isin(['RTP', 'ACH'])].copy()
            
            cashflows = []
            dates = []
            
            for idx, row in deposits.iterrows():
                try:
                    dt = pd.to_datetime(row['Settle Date'])
                    amt = row['Amount_Clean']
                    cashflows.append(-abs(amt))
                    dates.append(dt)
                except:
                    continue
            
            # Add Current Value
            dates.append(datetime.now())
            cashflows.append(float(current_value))
            xirr_val = calculate_xirr(cashflows, dates)
            
            # Create DataFrame for export
            xirr_df = pd.DataFrame({
                'Date': dates,
                'Amount': cashflows
            })
            if not xirr_df.empty:
                xirr_df['Date'] = pd.to_datetime(xirr_df['Date'])
                xirr_df = xirr_df.sort_values(by='Date')
                xirr_df['Date'] = xirr_df['Date'].dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error calculating XIRR: {e}")
            xirr_val = None

    # Use the correct variable names from the scope
    # Assuming inst_breakdown_dict is the dictionary of yearly breakdowns
    # Assuming overview_df is the investment overview dataframe
    
    last_trade_date_str = "N/A"
    type_col = cols_config.get("transaction_type", "Trans Code")
    if type_col in df.columns and settle_date_col in df.columns:
        trades_df = df[df[type_col] == 'Buy'].copy()
        if not trades_df.empty:
            trades_df['Parsed_Date'] = pd.to_datetime(trades_df[settle_date_col], errors='coerce')
            max_dt = trades_df['Parsed_Date'].max()
            if pd.notnull(max_dt):
                day = max_dt.day
                if 4 <= day <= 20 or 24 <= day <= 30:
                    suffix = "th"
                else:
                    suffix = ["st", "nd", "rd"][day % 10 - 1]
                last_trade_date_str = max_dt.strftime(f'{day}{suffix} of %B %Y')

    return {
        "Yearly_Summary_DF": final_yearly_summary,
        "Investment_Breakdown_Yearly": inst_breakdown_dict,
        "Investment_Overview_DF": overview_df,
        "XIRR": xirr_val,
        "XIRR_DF": xirr_df,
        "Last_Trade_Date": last_trade_date_str
    }


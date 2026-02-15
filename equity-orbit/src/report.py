import os
from datetime import datetime
from typing import Dict, Any

def generate_report(data_summary: Dict[str, Any], output_dir: str = "output", run_id: str = None) -> str:
    """
    Generates a markdown report from the summary data.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if run_id:
        report_filename = f"report_{run_id}.md"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"report_{timestamp}.md"
        
    report_filepath = os.path.join(output_dir, report_filename)

    with open(report_filepath, "w") as f:
        f.write(f"# Data Analysis Report\n")
        f.write(f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary Metrics\n")
        if "Yearly_Summary_DF" in data_summary:
            yearly_df = data_summary["Yearly_Summary_DF"].copy()
            
            # Extract Overall Net Total for the note
            net_total_overall = 0.0
            overall_row = yearly_df[yearly_df['Year'] == "Overall"]
            if not overall_row.empty:
                net_total_overall = overall_row['total_amount'].values[0]

            # Rename columns based on what's available
            col_map = {
                "Year": "Period",
                "total_amount": "Net Total ($)", 
                "total_buy_amount": "Total Buy ($)", 
                "total_dividends": "Dividends ($)", 
                "total_lending": "Lending ($)", 
                "total_invested": "Invested ($)", 
                "non_slip_count": "Trades",
                "unique_instruments": "Unique Inst."
            }
            yearly_df = yearly_df.rename(columns=col_map)
            
            # Select and reorder columns (Net Total is hidden from table)
            # Enable 'Invested ($)' as requested and placed it first
            columns_to_show = ["Period", "Invested ($)", "Total Buy ($)", "Dividends ($)", "Trades", "Unique Inst.", "Lending ($)"]
            
            # Filter only cols that exist
            cols_to_use = [c for c in columns_to_show if c in yearly_df.columns]
            display_df = yearly_df[cols_to_use].copy()

            # Format numeric columns
            money_cols = ["Invested ($)", "Total Buy ($)", "Dividends ($)", "Lending ($)"]
            for col in money_cols:
                if col in display_df.columns:
                    display_df[col] = display_df[col].map("${:,.2f}".format)
            
            f.write(display_df.to_markdown(index=False))
            f.write("\n\n")
            
            # Net Liquidity & Total Value Logic
            overall_row = yearly_df[yearly_df['Period'] == 'Overall']
            if not overall_row.empty:
                # Extract values (assuming they exist)
                net_liquidity = overall_row["Net Total ($)"].iloc[0] if "Net Total ($)" in overall_row.columns else 0.0
                total_buy = overall_row["Total Buy ($)"].iloc[0] if "Total Buy ($)" in overall_row.columns else 0.0
                total_div = overall_row["Dividends ($)"].iloc[0] if "Dividends ($)" in overall_row.columns else 0.0
                
                f.write(f"**Net Liquidity (Overall):** ${net_liquidity:,.2f}\n\n")
                
                # New line: Total Value (Buy + Div)
                total_value = total_buy + total_div
                f.write(f"**Total Value (Buy + Div):** ${total_value:,.2f}\n\n")

            # XIRR Display
            if "XIRR" in data_summary and data_summary["XIRR"] is not None:
                xirr = data_summary["XIRR"]
                f.write(f"**XIRR (Annualized Return):** {xirr * 100:.2f}%\n\n")
            
            # Add descriptions for the metrics
            f.write("**Metric Definitions:**\n")
            definitions = {
                "Invested ($)": "Total funds deposited (RTP transactions).",
                "Total Buy ($)": "Total capital spent on 'Buy' transactions.",
                "Dividends ($)": "Total dividend income received.",
                "Trades": "Total count of non-lending transactions executed.",
                "Unique Inst.": "Number of unique financial instruments (tickers).",
                "Lending ($)": "Income earned from stock lending programs (SLIP)."
            }
            for metric, desc in definitions.items():
                if metric in display_df.columns:
                    f.write(f"- **{metric}**: {desc}\n")
            f.write("\n")

        # Investment Overview Section
        if "Investment_Overview_DF" in data_summary:
            overview_df = data_summary["Investment_Overview_DF"]
            if not overview_df.empty:
                f.write("## Investment Overview\n")
                
                # Format for display
                display_overview = overview_df.copy()
                display_overview.columns = ["Category", "Invested Amount", "Percentage"]
                display_overview["Invested Amount"] = display_overview["Invested Amount"].map("${:,.2f}".format)
                display_overview["Percentage"] = display_overview["Percentage"].map("{:.1f}%".format)
                
                f.write(display_overview.to_markdown(index=False))
                f.write("\n\n")

        # Investment Breakdown Section
        if "Investment_Breakdown_Yearly" in data_summary:
            breakdown_dict = data_summary["Investment_Breakdown_Yearly"]
            
            f.write("## Investment Breakdown\n")
            
            # Helper to print table
            def print_inst_table(title, df, level="###"):
                if df is None or df.empty:
                    return
                
                # Calculate section total invested
                section_total = df['total_invested'].sum()
                
                f.write(f"{level} {title}\n")
                f.write(f"**Total Invested:** ${section_total:,.2f}\n\n")
                
                # Create a copy for display
                display_df = df.copy()
                
                # Check if 'Category' exists (added for Overall CSV) and drop it for the report table
                if 'Category' in display_df.columns:
                    display_df = display_df.drop(columns=['Category'])
                
                # Rename 'Company' to 'Instrument' as requested
                # The columns are [Ticker, Company, Invested, Quantity, Trades]
                display_df.columns = ["Ticker", "Instrument", "Invested ($)", "Quantity", "Trades"]
                display_df["Invested ($)"] = display_df["Invested ($)"].map("${:,.2f}".format)
                display_df["Quantity"] = display_df["Quantity"].map("{:.4f}".format)
                f.write(display_df.to_markdown(index=False))
                f.write("\n\n")

            # 1. Overall Portfolio (Requested to be first/above current year)

            if "Overall" in breakdown_dict:
                overall_df = breakdown_dict["Overall"]
                
                if "Category" in overall_df.columns:
                    # Grand Total for Overall Portfolio
                    grand_total = overall_df['total_invested'].sum()
                    f.write(f"### Overall Portfolio\n")
                    f.write(f"**Total Invested:** ${grand_total:,.2f}\n\n")

                    # Split into separate tables by Category
                    categories = sorted(overall_df['Category'].unique())
                    for cat in categories:
                        cat_df = overall_df[overall_df['Category'] == cat]
                        # Print sub-tables with deeper header level
                        print_inst_table(cat, cat_df, level="####")
                else:
                    # Fallback if no category column (shouldn't happen with current logic)
                    print_inst_table("Overall Portfolio", overall_df)

            # 2. Yearly Breakdowns (Descending)
            # Filter keys that are years (digits)
            years = [k for k in breakdown_dict.keys() if k.isdigit()]
            for year in sorted(years, key=int, reverse=True):
                print_inst_table(f"Year: {year}", breakdown_dict.get(year))

    return report_filepath

# Base structure - Implement the plan steps within this framework.
# Ensure all paths used are the absolute ones defined herein.
# You also need to explain to user how to understand or make sense of each analysis.
import pandas as pd
import os
import sys
import re # Import re, although not used in this specific plan, it's good practice if needed later
import codecs # Import codecs for potential encoding issues, although not directly used in the fix

# Error: 'tabulate' library might not be installed. Correction: Added try-except for import.
try:
    from tabulate import tabulate # Make sure tabulate is available
except ImportError:
    print("Warning: 'tabulate' library not found. Please install it (`pip install tabulate`). Using fallback print.")
    # Fallback print function if tabulate is missing
    def tabulate(data, headers='firstrow', tablefmt='simple', showindex=False, **kwargs):
        """Fallback basic print function if tabulate is not installed."""
        try:
            if headers == 'keys' and isinstance(data, pd.DataFrame):
                headers = data.columns.tolist()
            elif isinstance(data, pd.DataFrame):
                 headers = data.columns.tolist()

            print("\t".join(map(str, headers))) # Print header
            if isinstance(data, pd.DataFrame):
                for row in data.itertuples(index=showindex):
                     print("\t".join(map(str, row)))
            else: # Assuming list of lists or similar
                 for row in data:
                     print("\t".join(map(str, row)))
        except Exception as e_tab_fallback:
            print(f"Error in fallback tabulate: {repr(e_tab_fallback)}")


# --- Define ABSOLUTE path for input cleaned data ---
input_csv_path = r'D:/AI Data Analysis/output/data_processed.csv' # Raw string literal

# --- Define ABSOLUTE paths for output directories (though not used for saving in this script) ---
output_dir = r'D:/AI Data Analysis/output'
viz_plot_dir = os.path.join(output_dir, 'saved_plots')
trend_plot_dir = os.path.join(output_dir, 'trend_plots')

# --- Create output directories if they don't exist (good practice) ---
try:
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(viz_plot_dir, exist_ok=True)
    os.makedirs(trend_plot_dir, exist_ok=True)
except OSError as e_os:
    print(f"Warning: Could not create output directories: {repr(e_os)}")


# --- Set pandas display options ---
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 100) # Show more rows if needed

# Error: UnicodeEncodeError on print. Correction: Replaced special characters with ASCII alternatives.
print("**Starting Data Analysis Script**")
print(f"Input cleaned file: {input_csv_path}")

try:
    # --- Read the input CSV (cleaned data) using absolute path ---
    df = pd.read_csv(input_csv_path)
    print(f"Successfully loaded {input_csv_path}. Shape: {df.shape}")

    # === Implement Analysis Steps from Plan Here ===

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '❓' with '[?]'.
    print("\n**[?] Analysis 1: Distribution of Orders Across Platforms**")
    print("*   Interpretation: This shows the popularity or market share of each delivery platform (Jiomart, Blinkit, Swiggy Instamart) within this dataset.")
    try:
        platform_distribution = df['Platform'].value_counts().reset_index()
        platform_distribution.columns = ['Platform', 'Order Count'] # Rename columns for clarity
        if not platform_distribution.empty:
            print(tabulate(platform_distribution, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for platform distribution.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 1: {repr(e_key)} - 'Platform' column might be missing or mistyped.")
    except Exception as e_step1:
        print(f"Error during analysis step 1: {repr(e_step1)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '❓' with '[?]'.
    print("\n**[?] Analysis 2: Most Frequently Ordered Product Categories**")
    print("*   Interpretation: This identifies the product categories that are most in demand among customers.")
    try:
        category_frequency = df['Product Category'].value_counts().reset_index()
        category_frequency.columns = ['Product Category', 'Order Count'] # Rename columns
        category_frequency = category_frequency.sort_values('Order Count', ascending=False)
        if not category_frequency.empty:
            print("Top 10 Most Frequent Product Categories:")
            print(tabulate(category_frequency.head(10), headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for product category frequency.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 2: {repr(e_key)} - 'Product Category' column might be missing or mistyped.")
    except Exception as e_step2:
        print(f"Error during analysis step 2: {repr(e_step2)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '❓' with '[?]'.
    print("\n**[?] Analysis 3: Service Rating Distribution**")
    print("*   Interpretation: This gives an overview of general customer satisfaction. Are most customers happy (ratings 4-5), unhappy (ratings 1-2), or neutral (rating 3)?")
    try:
        rating_distribution = df['Service Rating'].value_counts().sort_index().reset_index()
        rating_distribution.columns = ['Service Rating', 'Count'] # Rename columns
        if not rating_distribution.empty:
            print(tabulate(rating_distribution, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for service rating distribution.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 3: {repr(e_key)} - 'Service Rating' column might be missing or mistyped.")
    except Exception as e_step3:
        print(f"Error during analysis step 3: {repr(e_step3)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '💡' with '[!]'.
    print("\n**[!] Analysis 4: Average Order Value (INR) per Platform**")
    print("*   Interpretation: This helps understand if customers tend to place higher or lower value orders on specific platforms.")
    try:
        avg_value_platform = df.groupby('Platform')['Order Value (INR)'].mean().reset_index()
        avg_value_platform.columns = ['Platform', 'Average Order Value (INR)'] # Rename columns
        if not avg_value_platform.empty:
            print(tabulate(avg_value_platform, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for average order value per platform.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 4: {repr(e_key)} - 'Platform' or 'Order Value (INR)' column might be missing or mistyped.")
    except Exception as e_step4:
        print(f"Error during analysis step 4: {repr(e_step4)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '💡' with '[!]'.
    print("\n**[!] Analysis 5: Average Delivery Time (Minutes) per Platform**")
    print("*   Interpretation: This compares the average delivery speed across different platforms, indicating potential operational efficiency differences.")
    try:
        avg_time_platform = df.groupby('Platform')['Delivery Time (Minutes)'].mean().reset_index()
        avg_time_platform.columns = ['Platform', 'Average Delivery Time (Minutes)'] # Rename columns
        if not avg_time_platform.empty:
            print(tabulate(avg_time_platform, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for average delivery time per platform.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 5: {repr(e_key)} - 'Platform' or 'Delivery Time (Minutes)' column might be missing or mistyped.")
    except Exception as e_step5:
        print(f"Error during analysis step 5: {repr(e_step5)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '💡' with '[!]'.
    print("\n**[!] Analysis 6: Average Service Rating per Platform**")
    print("*   Interpretation: This indicates which platforms generally receive better customer satisfaction scores.")
    try:
        avg_rating_platform = df.groupby('Platform')['Service Rating'].mean().reset_index()
        avg_rating_platform.columns = ['Platform', 'Average Service Rating'] # Rename columns
        if not avg_rating_platform.empty:
            print(tabulate(avg_rating_platform, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for average service rating per platform.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 6: {repr(e_key)} - 'Platform' or 'Service Rating' column might be missing or mistyped.")
    except Exception as e_step6:
        print(f"Error during analysis step 6: {repr(e_step6)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '📈' with '[>]'.
    print("\n**[>] Analysis 7: Average Order Value (INR) by Product Category**")
    print("*   Interpretation: This reveals which product categories typically involve higher spending per order.")
    try:
        avg_value_category = df.groupby('Product Category')['Order Value (INR)'].mean().reset_index()
        avg_value_category.columns = ['Product Category', 'Average Order Value (INR)'] # Rename columns
        avg_value_category = avg_value_category.sort_values('Average Order Value (INR)', ascending=False)
        if not avg_value_category.empty:
            # Error: Potential large output. Correction: Limit output with .head() or print full if small.
            if len(avg_value_category) > 20:
                 print("Top 20 Categories by Average Order Value:")
                 print(tabulate(avg_value_category.head(20), headers='keys', tablefmt='psql', showindex=False))
            else:
                 print(tabulate(avg_value_category, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for average order value by product category.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 7: {repr(e_key)} - 'Product Category' or 'Order Value (INR)' column might be missing or mistyped.")
    except Exception as e_step7:
        print(f"Error during analysis step 7: {repr(e_step7)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '📈' with '[>]'.
    print("\n**[>] Analysis 8: Relationship between Service Rating and Average Delivery Time**")
    print("*   Interpretation: This explores if lower ratings are associated with longer delivery times, or if higher ratings correlate with faster deliveries.")
    try:
        rating_vs_time = df.groupby('Service Rating')['Delivery Time (Minutes)'].mean().reset_index()
        rating_vs_time.columns = ['Service Rating', 'Average Delivery Time (Minutes)'] # Rename columns
        if not rating_vs_time.empty:
            print(tabulate(rating_vs_time, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for relationship between service rating and delivery time.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 8: {repr(e_key)} - 'Service Rating' or 'Delivery Time (Minutes)' column might be missing or mistyped.")
    except Exception as e_step8:
        print(f"Error during analysis step 8: {repr(e_step8)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '❓' with '[?]'.
    print("\n**[?] Analysis 9: Most Common Customer Feedback per Service Rating**")
    print("*   Interpretation: This provides qualitative insight into *why* customers give certain ratings, linking specific feedback phrases to satisfaction levels.")
    try:
        # Define a function to safely get the mode, handling potential empty series or multiple modes
        def get_mode_safe(x):
            # Drop NaN values before calculating mode to avoid issues
            x = x.dropna()
            if x.empty:
                return 'N/A'
            modes = x.mode()
            if not modes.empty:
                # Join multiple modes with a separator if they exist
                return ' | '.join(modes.astype(str))
            return 'N/A' # Return 'N/A' if no mode (e.g., all unique values or empty group after dropna)

        # Ensure Customer Feedback is treated as string
        df['Customer Feedback'] = df['Customer Feedback'].astype(str)

        common_feedback = df.groupby('Service Rating')['Customer Feedback'].agg(get_mode_safe).reset_index()
        common_feedback.columns = ['Service Rating', 'Most Common Feedback'] # Rename columns
        if not common_feedback.empty:
            print(tabulate(common_feedback, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for common customer feedback per rating.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 9: {repr(e_key)} - 'Service Rating' or 'Customer Feedback' column might be missing or mistyped.")
    except Exception as e_step9:
        print(f"Error during analysis step 9: {repr(e_step9)}")

    # Error: UnicodeEncodeError on print. Correction: Replaced special character '📈' with '[>]'.
    print("\n**[>] Analysis 10: Consolidated Platform Performance Metrics**")
    print("*   Interpretation: This gives a multi-dimensional view of each platform's performance across key metrics (value, speed, satisfaction) for easy comparison.")
    try:
        # Ensure necessary columns are numeric before aggregation
        numeric_cols = ['Order Value (INR)', 'Delivery Time (Minutes)', 'Service Rating']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce') # Convert non-numeric to NaN

        platform_performance = df.groupby('Platform').agg(
            Average_Order_Value=('Order Value (INR)', 'mean'),
            Average_Delivery_Time=('Delivery Time (Minutes)', 'mean'),
            Average_Service_Rating=('Service Rating', 'mean')
        ).reset_index()
        # Rename columns for clarity in the table
        platform_performance.columns = ['Platform', 'Avg Order Value (INR)', 'Avg Delivery Time (Min)', 'Avg Service Rating']
        if not platform_performance.empty:
            print(tabulate(platform_performance, headers='keys', tablefmt='psql', showindex=False))
        else:
            print("No data found for consolidated platform performance.")
    except KeyError as e_key:
        print(f"KeyError during analysis step 10: {repr(e_key)} - One or more required columns ('Platform', 'Order Value (INR)', 'Delivery Time (Minutes)', 'Service Rating') might be missing or mistyped.")
    except Exception as e_step10:
        print(f"Error during analysis step 10: {repr(e_step10)}")

    # === End of Analysis Steps ===

except FileNotFoundError:
    print(f"FATAL ERROR: Input file '{input_csv_path}' not found. Make sure the cleaning step ran successfully and saved the file correctly.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"FATAL ERROR: Input file '{input_csv_path}' is empty.")
    sys.exit(1)
except ImportError as e_imp: # Catch specific import error for tabulate maybe
    print(f"FATAL ERROR: Required library not installed: {e_imp}. Cannot proceed with analysis.")
    sys.exit(1)
except Exception as e:
    # Error: UnicodeEncodeError could occur here if repr(e) contains problematic chars.
    # Correction: Try to encode the error message safely for printing.
    try:
        error_message = f"An unexpected error occurred during data analysis setup or execution: {repr(e)}"
        print(error_message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    except Exception as e_print:
        print(f"An unexpected error occurred, and printing the error details failed: {e_print}")
    # raise e # Uncomment for detailed traceback during development
    sys.exit(1) # Exit after a major unexpected error

print("\n**Finished Data Analysis Script**")
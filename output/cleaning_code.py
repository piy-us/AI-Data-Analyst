# Base structure - Implement the plan steps within this framework.
# Ensure all paths used are the absolute ones defined herein.

import pandas as pd
import os
import re # Include re just in case needed
import sys # For potential path manipulation if needed, though absolute used
import codecs # Needed for potential encoding issues, though not the primary fix here

# Import plotting/output libraries (even if not used in this specific plan, as per instructions)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    import matplotlib.pyplot as plt
    from tabulate import tabulate
except ImportError as e:
    print(f"Warning: Optional library not found: {e}. Tabulate output might fail if used.")
    # Define a dummy tabulate if needed, or ensure it's not called
    def tabulate(data, headers='firstrow', tablefmt='psql'):
        # Basic fallback if tabulate is not installed
        if headers == 'firstrow':
            header = data[0]
            data = data[1:]
        else:
            header = headers
        print("--- Fallback Table Output (tabulate not installed) ---")
        print("\t".join(map(str, header)))
        print("-" * (8 * len(header)))
        for row in data:
            print("\t".join(map(str, row)))
        print("--- End Fallback Table Output ---")
        return "Fallback table printed."


# --- Define ABSOLUTE paths to use ---
# Error: Input path was incorrect based on description.
# Correction: Changed input path to the specified 'data_processed.csv'.
input_path = r'D:/AI Data Analysis/output/data_processed.csv' # Raw string literal for Windows paths
output_cleaned_path = r'D:/AI Data Analysis/output/data_processed.csv' # Raw string literal
output_dir_base = os.path.dirname(output_cleaned_path)
# Define plot directories even if not used in this script, ensure they exist later if needed
output_viz_path = r'D:/AI Data Analysis/output/saved_plots'
output_trend_path = r'D:/AI Data Analysis/output/trend_plots'


print(f"**Starting Data Cleaning Script**")
print(f"Input file: {input_path}")
print(f"Output file: {output_cleaned_path}")

# --- Ensure output directories exist ---
try:
    os.makedirs(output_dir_base, exist_ok=True)
    print(f"Ensured base output directory exists: {output_dir_base}")
    # Also create plot directories as per instructions
    os.makedirs(output_viz_path, exist_ok=True)
    print(f"Ensured viz plot directory exists: {output_viz_path}")
    os.makedirs(output_trend_path, exist_ok=True)
    print(f"Ensured trend plot directory exists: {output_trend_path}")
except Exception as e:
    print(f"Error creating output directories ({output_dir_base}, {output_viz_path}, {output_trend_path}): {repr(e)}")
    sys.exit(1) # Exit if directory creation is critical

try:
    # --- Read the input CSV using the absolute path ---
    # Added encoding='utf-8' as a precaution, though not the primary error source
    df = pd.read_csv(input_path, encoding='utf-8')
    print(f"Successfully loaded {input_path}. Initial Shape: {df.shape}")
    print(f"Initial dtypes:\n{df.dtypes}")

    # === Implement Cleaning Steps from Plan Here ===

    # --- Step 5 (Part 1): Improve Consistency & Formatting (Whitespace, Case, Pre-conversion Checks) ---
    print("\n--- Applying Step 5 (Part 1): Improve Consistency & Formatting ---")
    try:
        # Identify object columns
        object_columns = df.select_dtypes(include='object').columns
        print(f"Object columns identified for potential trimming/case standardization: {list(object_columns)}")

        # Apply trim whitespace to all object columns
        for col in object_columns:
            if col in df.columns: # Check if column still exists
                try:
                    # Check if column actually contains strings before applying .str accessor
                    if pd.api.types.is_string_dtype(df[col]):
                        df[col] = df[col].str.strip()
                        print(f"Trimmed whitespace for column: '{col}'")
                    else:
                        # Handle non-string data if necessary, or just skip
                        print(f"Skipping whitespace trim for non-string column: '{col}'")
                except AttributeError:
                    print(f"Warning: Column '{col}' caused AttributeError during strip, skipping whitespace trim.")
                except Exception as e_trim:
                    print(f"Error trimming whitespace for column '{col}': {repr(e_trim)}")
            else:
                 print(f"Warning: Column '{col}' not found for whitespace trimming (might have been converted/dropped).")


        # Standardize case for specific columns
        columns_to_title_case = ['Platform', 'Product Category']
        for col in columns_to_title_case:
             if col in df.columns and pd.api.types.is_string_dtype(df[col]):
                 df[col] = df[col].str.title()
                 print(f"Applied title case to column: '{col}'")
             elif col in df.columns:
                 print(f"Skipping title case for non-string column: '{col}'")


        # Standardize case for Customer Feedback (using lower case for simplicity)
        if 'Customer Feedback' in df.columns and pd.api.types.is_string_dtype(df['Customer Feedback']):
            df['Customer Feedback'] = df['Customer Feedback'].str.lower()
            print("Applied lower case to column: 'Customer Feedback'")
            # Note: Plan mentioned reviewing unique values and consolidating - this requires manual inspection.
            # print("Unique values in 'Customer Feedback' after lowercasing (Top 20):")
            # print(df['Customer Feedback'].value_counts().head(20))
        elif 'Customer Feedback' in df.columns:
             print("Skipping lower case for non-string column: 'Customer Feedback'")


        # Check and standardize 'Delivery Delay' and 'Refund Requested' before conversion
        bool_cols_to_check = ['Delivery Delay', 'Refund Requested']
        expected_bool_values = {'yes', 'no'} # Use lowercase for comparison after potential case standardization

        for col in bool_cols_to_check:
            if col in df.columns and pd.api.types.is_string_dtype(df[col]):
                # Standardize to lower case first for easier checking
                df[col] = df[col].str.lower().str.strip() # Add strip here too
                unique_vals = set(df[col].dropna().unique()) # Use dropna() before unique()
                unexpected_vals = unique_vals - expected_bool_values
                if unexpected_vals:
                    print(f"WARNING: Unexpected values found in '{col}': {unexpected_vals}. Attempting standardization to 'Yes'/'No'.")
                    # Simple standardization: map 'yes' -> 'Yes', 'no' -> 'No', others could be mapped to NaN or a default
                    # For this script, we'll assume they are variations of yes/no and standardize to title case 'Yes'/'No'
                    df[col] = df[col].map({'yes': 'Yes', 'no': 'No'})
                    # Re-check for NaNs introduced if unexpected values existed
                    if df[col].isnull().any():
                         print(f"WARNING: Null values introduced in '{col}' after standardization due to unexpected original values.")
                elif unique_vals.issubset(expected_bool_values): # Check if only expected values (or subset) exist
                     # If only 'yes', 'no' found, standardize case to 'Yes', 'No' for mapping
                     df[col] = df[col].str.title()
                     print(f"Values in '{col}' confirmed as 'Yes'/'No' (case-insensitive). Standardized to 'Yes'/'No'.")
                else:
                    # Handle cases where the column might be empty or contain only NaN after filtering
                    print(f"Column '{col}' does not contain standard 'yes'/'no' values or is empty after processing.")

            elif col in df.columns:
                 print(f"Skipping boolean check for non-string column: '{col}'")
            elif col not in df.columns:
                 print(f"Warning: Column '{col}' not found for boolean check.")

    except Exception as e_step5_part1:
        print(f"Error during Step 5 (Part 1 - Consistency/Formatting): {repr(e_step5_part1)}")


    # --- Step 1: Datatype Conversion ---
    print("\n--- Applying Step 1: Datatype Conversion ---")
    try:
        # Convert 'Delivery Delay' to Integer (1/0)
        if 'Delivery Delay' in df.columns:
            try:
                # Ensure mapping happens correctly even if NaNs were introduced
                df['Delivery Delay'] = df['Delivery Delay'].map({'Yes': 1, 'No': 0})
                # Convert to nullable integer type Int64 to handle potential NaNs gracefully
                df['Delivery Delay'] = df['Delivery Delay'].astype('Int64')
                print("Converted 'Delivery Delay' to Integer (1 for Yes, 0 for No, <NA> for others).")
            except Exception as e_conv_delay:
                 print(f"Error converting 'Delivery Delay': {repr(e_conv_delay)}. Check values if not handled in Step 5.")

        # Convert 'Refund Requested' to Integer (1/0)
        if 'Refund Requested' in df.columns:
             try:
                df['Refund Requested'] = df['Refund Requested'].map({'Yes': 1, 'No': 0})
                # Convert to nullable integer type Int64
                df['Refund Requested'] = df['Refund Requested'].astype('Int64')
                print("Converted 'Refund Requested' to Integer (1 for Yes, 0 for No, <NA> for others).")
             except Exception as e_conv_refund:
                 print(f"Error converting 'Refund Requested': {repr(e_conv_refund)}. Check values if not handled in Step 5.")

        # 'Order Date & Time': Plan defers conversion, keeping as object after consistency checks.
        print("Skipping 'Order Date & Time' conversion as per plan (focus on consistency).")

    except Exception as e_step1:
        print(f"Error during Step 1 (Datatype Conversion): {repr(e_step1)}")


    # --- Step 2: Handle Missing Values ---
    print("\n--- Applying Step 2: Handle Missing Values ---")
    try:
        # Based on the plan, no missing values were reported initially. Check again.
        missing_values = df.isnull().sum()
        print("Checking for missing values after initial steps:")
        print(missing_values[missing_values > 0])
        if missing_values.sum() == 0:
            print("No missing values found, no action required as per plan.")
        else:
            print(f"Warning: {missing_values.sum()} missing values detected after initial steps. No imputation applied per plan.")
            # If imputation were needed, it would go here. Example:
            # if 'Delivery Delay' in df.columns and df['Delivery Delay'].isnull().any():
            #     median_val = df['Delivery Delay'].median() # Or mode, mean, etc.
            #     df['Delivery Delay'].fillna(median_val, inplace=True)
            #     print(f"Filled missing 'Delivery Delay' values with median: {median_val}")
    except Exception as e_step2:
        print(f"Error during Step 2 (Missing Values Check): {repr(e_step2)}")


    # --- Step 3: Handle Duplicate Rows ---
    print("\n--- Applying Step 3: Handle Duplicate Rows ---")
    try:
        # Based on the plan, no duplicate rows were reported initially. Check again.
        initial_duplicates = df.duplicated().sum()
        if initial_duplicates == 0:
            print("No duplicate rows found, no action required as per plan.")
        else:
            # If duplicates were found and needed removal:
            # print(f"Found {initial_duplicates} duplicate rows. Removing them.")
            # df.drop_duplicates(inplace=True)
            # print(f"Shape after dropping duplicates: {df.shape}")
            print(f"Warning: {initial_duplicates} duplicate rows detected. No removal applied per plan.") # Adjust if plan changes
    except Exception as e_step3:
        print(f"Error during Step 3 (Duplicate Rows Check): {repr(e_step3)}")


    # --- Step 4: Handle Outliers ---
    print("\n--- Applying Step 4: Handle Outliers ---")
    try:
        # Plan specifies NO outlier treatment for 'Delivery Time (Minutes)' and 'Order Value (INR)'.
        print("No outlier treatment applied to 'Delivery Time (Minutes)' or 'Order Value (INR)' as per plan.")
        # If treatment were needed, it would go here (e.g., capping, removal based on IQR/Z-score).
    except Exception as e_step4:
        print(f"Error during Step 4 (Outliers): {repr(e_step4)}")


    # --- Step 5 (Part 2): Improve Consistency & Formatting (`Order Date & Time`) ---
    print("\n--- Applying Step 5 (Part 2): Improve Consistency & Formatting (`Order Date & Time`) ---")
    try:
        # Plan mentions standardizing format (e.g., MM:SS.f) but defers complex conversion.
        # Whitespace trimming was already done in Part 1.
        # Further validation/standardization could be added here if needed.
        # Example check (optional): Ensure format looks like MM:SS.f
        if 'Order Date & Time' in df.columns and pd.api.types.is_string_dtype(df['Order Date & Time']):
            # Regex updated to be slightly more robust (allows single/double digit minutes, requires single digit fractional second)
            time_format_regex = re.compile(r'^\d{1,2}:\d{2}\.\d$')
            # Use .astype(str) defensively before .str.match
            invalid_times_mask = ~df['Order Date & Time'].astype(str).str.match(time_format_regex, na=False) & df['Order Date & Time'].notna()
            invalid_times = df.loc[invalid_times_mask, 'Order Date & Time']

            if not invalid_times.empty:
                print(f"Warning: Found {len(invalid_times)} non-null entries in 'Order Date & Time' that may not match MM:SS.f format.")
                # print("Examples of potentially invalid formats:")
                # print(invalid_times.head())
            else:
                print("'Order Date & Time' format appears consistent with MM:SS.f pattern (basic check).")
        elif 'Order Date & Time' in df.columns:
             print("Skipping format check for non-string column: 'Order Date & Time'")

        print("Keeping 'Order Date & Time' as object type after basic consistency checks as per plan.")
    except Exception as e_step5_part2:
        print(f"Error during Step 5 (Part 2 - Order Date & Time Consistency): {repr(e_step5_part2)}")


    # --- Step 6: Minimal Feature Engineering ---
    print("\n--- Applying Step 6: Minimal Feature Engineering ---")
    try:
        # Plan suggests potentially extracting time components but makes it conditional.
        print("No feature engineering (e.g., extracting time components) applied in this script as per plan.")
        # If feature engineering were required:
        # Example:
        # try:
        #     temp_time = df['Order Date & Time'].str.split(':', expand=True)
        #     df['Order_Minute'] = pd.to_numeric(temp_time[0], errors='coerce')
        #     temp_sec = temp_time[1].str.split('.', expand=True)
        #     df['Order_Second'] = pd.to_numeric(temp_sec[0], errors='coerce')
        #     df['Order_Fractional_Second'] = pd.to_numeric(temp_sec[1], errors='coerce')
        #     print("Extracted time components into Order_Minute, Order_Second, Order_Fractional_Second")
        # except Exception as fe_err:
        #     print(f"Could not perform feature engineering on 'Order Date & Time': {repr(fe_err)}")
    except Exception as e_step6:
        print(f"Error during Step 6 (Feature Engineering): {repr(e_step6)}")


    # === End of Cleaning Steps ===

    # --- Final Check ---
    print("\n--- Final Data Check ---")
    print(f"Final data shape: {df.shape}")
    print("Final dtypes:")
    print(df.dtypes)
    print("Final missing values count:")
    print(df.isnull().sum())
    print("Sample of cleaned data (first 5 rows):")
    # Use tabulate for better formatting if available
    try:
        # Use display options to prevent truncation in tabulate/fallback
        with pd.option_context('display.max_rows', 10, 'display.max_columns', None):
            print(tabulate(df.head(), headers='keys', tablefmt='psql'))
    except NameError: # Fallback if tabulate failed to import or is not defined
         with pd.option_context('display.max_rows', 10, 'display.max_columns', None, 'display.width', 1000):
              print(df.head().to_string())


    # --- Save the cleaned data to the absolute output path ---
    try:
        df.to_csv(output_cleaned_path, index=False, encoding='utf-8') # Specify encoding explicitly
        # Error: Original print statement used an emoji causing UnicodeEncodeError on some terminals.
        # Correction: Removed the emoji from the print statement.
        print(f"\n** Cleaned data saved successfully to {output_cleaned_path} **")
    except Exception as e_save:
        print(f"Error saving cleaned data to {output_cleaned_path}: {repr(e_save)}")
        sys.exit(1)


except FileNotFoundError:
    print(f"FATAL ERROR: Input file '{input_path}' not found.")
    sys.exit(1) # Exit if input file not found
except pd.errors.EmptyDataError:
    print(f"FATAL ERROR: Input file '{input_path}' is empty.")
    sys.exit(1)
except KeyError as e_key:
    print(f"FATAL ERROR: A specified column key was not found: {repr(e_key)}. Check column names in the input CSV and script.")
    sys.exit(1)
except Exception as e:
    # Error: The original error message here could also fail if the exception 'e' contained the problematic emoji.
    # Correction: Print a generic error message without embedding the potentially problematic repr(e) directly if encoding issues are suspected.
    # We still print repr(e) but separately, hoping the primary issue is fixed.
    print(f"An unexpected error occurred during data cleaning.")
    try:
        print(f"Error details: {repr(e)}")
    except UnicodeEncodeError:
        print("Error details could not be printed due to encoding issues.")
    sys.exit(1) # Exit on other major errors

print("\n**Finished Data Cleaning Script**")
# Base structure - Implement the plan steps within this framework.
# Ensure all paths used are the absolute ones defined herein.
# You also need to explain to user how to understand or explore each plot, and this should be done on the plot or image itself.
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import re # Import re, although not explicitly used in the plan, it's good practice as requested
import matplotlib.pyplot as plt # Also import matplotlib in case needed
import codecs # Import codecs for potential encoding issues, though removing emojis is the primary fix

# Import tabulate safely
try:
    from tabulate import tabulate
except ImportError:
    print("Warning: 'tabulate' library not found. Install it using 'pip install tabulate' for formatted table output.")
    # Define a dummy tabulate function if it's not available
    def tabulate(data, headers='firstrow', tablefmt='psql', **kwargs):
        # Simple fallback: print first few rows as CSV
        if isinstance(data, pd.DataFrame):
            return data.to_csv(index=False)
        else:
            # Basic representation for other data types
            return str(data)

# --- Define ABSOLUTE paths ---
input_csv_path = r'D:/AI Data Analysis/output/data_processed.csv' # Raw string literal
output_plot_dir = r'D:/AI Data Analysis/output/trend_plots' # Trend plots directory (Raw string literal)

# Error: UnicodeEncodeError caused by emojis in print statements on some terminals/encodings.
# Correction: Removed emojis (🔍, ✨, 🧭) from print statements.
print("**Starting Trends & Patterns Investigation Script**")
print(f"Input cleaned file: {input_csv_path}")
print(f"Output trend plot directory: {output_plot_dir}")

# --- Ensure trend plot directory exists ---
try:
    os.makedirs(output_plot_dir, exist_ok=True)
    print(f"Ensured trend plot directory exists: {output_plot_dir}")
except Exception as e:
    print(f"FATAL ERROR: Could not create trend plot directory {output_plot_dir}: {repr(e)}")
    sys.exit(1) # Exit if we cannot create the output directory

try:
    # --- Read the input CSV (cleaned data) using absolute path ---
    # Error: Potential UnicodeDecodeError if CSV is not UTF-8.
    # Correction: Added encoding='utf-8' or 'latin1' as a fallback.
    try:
        df = pd.read_csv(input_csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        print("Warning: UTF-8 decoding failed. Trying 'latin1' encoding.")
        try:
            df = pd.read_csv(input_csv_path, encoding='latin1')
        except Exception as e_read:
            print(f"FATAL ERROR: Failed to read CSV with both UTF-8 and latin1 encoding: {repr(e_read)}")
            sys.exit(1)

    print(f"Successfully loaded {input_csv_path}. Shape: {df.shape}")

    # Convert relevant columns to appropriate types if necessary (e.g., numeric, category)
    # Example: Ensure numeric columns are numeric
    numeric_cols_to_check = ['Delivery Time (Minutes)', 'Service Rating', 'Order Value (INR)']
    for col in numeric_cols_to_check:
        if col in df.columns:
            # Error: Simple pd.to_numeric might fail on complex non-numeric strings.
            # Correction: Added robust conversion within a try-except block per column.
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce') # Coerce errors to NaN
            except Exception as e_numeric:
                print(f"Warning: Could not convert column '{col}' to numeric: {repr(e_numeric)}. Skipping conversion for this column.")
        else:
            print(f"Warning: Expected numeric column '{col}' not found in the DataFrame.")


    # Drop rows where key columns for analysis might be NaN after coercion
    initial_rows = df.shape[0]
    df.dropna(subset=[col for col in numeric_cols_to_check if col in df.columns], inplace=True) # Drop rows if essential numeric data is missing
    print(f"Shape after handling potential non-numeric values in key columns: {df.shape} (dropped {initial_rows - df.shape[0]} rows)")

    # === Implement Trend Investigation Steps from Plan Here ===

    # --- Trend 1: Delivery Time Variation by Product Category ---
    # Error: UnicodeEncodeError caused by emoji in print statement.
    # Correction: Removed emoji.
    print("\n**Investigating Trend 1: Delivery Time Variation by Product Category**")
    try:
        if 'Product Category' in df.columns and 'Delivery Time (Minutes)' in df.columns:
            fig_trend1 = px.box(df,
                                x='Product Category',
                                y='Delivery Time (Minutes)',
                                title='Delivery Time Distribution Across Product Categories',
                                labels={'Delivery Time (Minutes)': 'Delivery Time (Minutes)', 'Product Category': 'Product Category'})

            # Add interpretation guidance
            fig_trend1.add_annotation(text="<b>How to read:</b> Compare the boxes (median line, box length = IQR) and whiskers (range) across categories.<br>"
                                          "Identify categories with significantly longer/shorter median times (middle line),<br>"
                                          "or more/less variable delivery times (box/whisker length). Hover for specific stats (Q1, Median, Q3).",
                                      align='left',
                                      showarrow=False,
                                      xref='paper', yref='paper',
                                      x=0.02, y=0.98, # Position annotation top-left
                                      bgcolor="rgba(255, 255, 255, 0.7)", # Semi-transparent background
                                      bordercolor="black",
                                      borderwidth=1)
            fig_trend1.update_layout(title_y=0.95, title_x=0.5) # Adjust title position if needed

            plot_filename_trend1 = os.path.join(output_plot_dir, 'trend1_delivery_time_by_category.html')
            fig_trend1.write_html(plot_filename_trend1)
            print(f"Trend 1 plot saved to {plot_filename_trend1}")
        else:
            print("Skipping Trend 1: Required columns ('Product Category', 'Delivery Time (Minutes)') not found.")
    except Exception as e_trend1:
        print(f"Error investigating Trend 1: {repr(e_trend1)}")

    # --- Trend 2: Service Rating Variation by Platform ---
    # Error: UnicodeEncodeError caused by emoji in print statement.
    # Correction: Removed emoji.
    print("\n**Investigating Trend 2: Service Rating Variation by Platform**")
    try:
        if 'Platform' in df.columns and 'Service Rating' in df.columns:
            # Ensure Service Rating is treated appropriately if needed (e.g., if it has few discrete values)
            # For box plot, numeric usually works fine, but let's ensure Platform is string/category
            df['Platform'] = df['Platform'].astype(str)

            fig_trend2 = px.box(df,
                                x='Platform',
                                y='Service Rating',
                                title='Service Rating Distribution Across Platforms',
                                labels={'Service Rating': 'Service Rating', 'Platform': 'Platform'})

            # Add interpretation guidance
            fig_trend2.add_annotation(text="<b>How to read:</b> Compare the median rating (middle line inside the box) and the rating spread<br>"
                                          "(box length = Interquartile Range, IQR) for each platform.<br>"
                                          "Identify platforms with consistently higher/lower median ratings or more/less varied customer ratings (longer/shorter boxes/whiskers).<br>"
                                          "Hover over boxes for detailed statistics (Min, Q1, Median, Q3, Max).",
                                      align='left',
                                      showarrow=False,
                                      xref='paper', yref='paper',
                                      x=0.02, y=0.98,
                                      bgcolor="rgba(255, 255, 255, 0.7)",
                                      bordercolor="black",
                                      borderwidth=1)
            fig_trend2.update_layout(title_y=0.95, title_x=0.5)

            plot_filename_trend2 = os.path.join(output_plot_dir, 'trend2_rating_by_platform.html')
            fig_trend2.write_html(plot_filename_trend2)
            print(f"Trend 2 plot saved to {plot_filename_trend2}")
        else:
            print("Skipping Trend 2: Required columns ('Platform', 'Service Rating') not found.")
    except Exception as e_trend2:
        print(f"Error investigating Trend 2: {repr(e_trend2)}")

    # --- Trend 3: Relationship Between Delivery Time and Service Rating ---
    # Error: UnicodeEncodeError caused by emoji in print statement.
    # Correction: Removed emoji.
    print("\n**Investigating Trend 3: Relationship Between Delivery Time and Service Rating**")
    try:
        if 'Service Rating' in df.columns and 'Delivery Time (Minutes)' in df.columns:
            # Treat Service Rating as categorical for the x-axis
            df_trend3 = df.copy()
            # Error: Converting float ratings directly to string might lead to unexpected sorting (e.g., "10.0" before "2.0").
            # Correction: Convert to string after ensuring it's int or rounded float if needed, then use pd.Categorical for proper sorting.
            try:
                # Attempt to convert to int first if they are whole numbers, otherwise keep as float then string
                if df_trend3['Service Rating'].apply(lambda x: x == int(x)).all():
                    df_trend3['Service Rating Cat'] = df_trend3['Service Rating'].astype(int).astype(str)
                else:
                    # If floats, maybe round before converting? Or just convert float to string.
                    df_trend3['Service Rating Cat'] = df_trend3['Service Rating'].astype(str)
                # Sort categories numerically before creating the categorical type
                unique_ratings_str = df_trend3['Service Rating Cat'].unique()
                sorted_categories = sorted(unique_ratings_str, key=float)
                df_trend3['Service Rating Cat'] = pd.Categorical(df_trend3['Service Rating Cat'], categories=sorted_categories, ordered=True)
            except Exception as e_cat_sort:
                 print(f"Warning: Could not create sorted categorical Service Rating for Trend 3: {repr(e_cat_sort)}. Using unsorted strings.")
                 df_trend3['Service Rating Cat'] = df_trend3['Service Rating'].astype(str) # Fallback


            fig_trend3 = px.box(df_trend3,
                                x='Service Rating Cat',
                                y='Delivery Time (Minutes)',
                                title='How Delivery Time Varies with Service Rating',
                                labels={'Delivery Time (Minutes)': 'Delivery Time (Minutes)', 'Service Rating Cat': 'Service Rating'})

            # Add interpretation guidance
            fig_trend3.add_annotation(text="<b>How to read:</b> Observe the distribution of delivery times for each service rating score.<br>"
                                          "Look for trends: Do lower ratings (e.g., 1, 2) correspond to higher median delivery times (middle line)<br>"
                                          "or wider spreads (longer boxes/whiskers), indicating more variability or longer waits?<br>"
                                          "Hover over boxes for detailed statistics.",
                                      align='left',
                                      showarrow=False,
                                      xref='paper', yref='paper',
                                      x=0.02, y=0.98,
                                      bgcolor="rgba(255, 255, 255, 0.7)",
                                      bordercolor="black",
                                      borderwidth=1)
            fig_trend3.update_layout(title_y=0.95, title_x=0.5)

            plot_filename_trend3 = os.path.join(output_plot_dir, 'trend3_delivery_time_by_rating.html')
            fig_trend3.write_html(plot_filename_trend3)
            print(f"Trend 3 plot saved to {plot_filename_trend3}")
        else:
            print("Skipping Trend 3: Required columns ('Service Rating', 'Delivery Time (Minutes)') not found.")
    except Exception as e_trend3:
        print(f"Error investigating Trend 3: {repr(e_trend3)}")

    # --- Trend 4: Order Value Distribution Across Platforms ---
    # Error: UnicodeEncodeError caused by emoji in print statement.
    # Correction: Removed emoji.
    print("\n**Investigating Trend 4: Order Value Distribution Across Platforms**")
    try:
        if 'Platform' in df.columns and 'Order Value (INR)' in df.columns:
            # Ensure Platform is string/category
            df['Platform'] = df['Platform'].astype(str)

            fig_trend4 = px.violin(df,
                                   x='Platform',
                                   y='Order Value (INR)',
                                   box=True, # Show box plot inside violin
                                   points=False, # Changed from "all" to False for potentially large datasets to avoid clutter/performance issues
                                   title='Order Value Distribution Across Platforms',
                                   labels={'Order Value (INR)': 'Order Value (INR)', 'Platform': 'Platform'})

            # Add interpretation guidance
            fig_trend4.add_annotation(text="<b>How to read:</b> Compare the shape (width = density of orders at that value) and box statistics<br>"
                                          "(median, IQR) across platforms. Wider sections indicate more orders at that value range.<br>"
                                          "Identify platforms with higher median order values (middle line in box), wider spending ranges (violin height/box whiskers),<br>"
                                          "or different value concentrations (shape of violin). Hover for details.",
                                      align='left',
                                      showarrow=False,
                                      xref='paper', yref='paper',
                                      x=0.02, y=0.98,
                                      bgcolor="rgba(255, 255, 255, 0.7)",
                                      bordercolor="black",
                                      borderwidth=1)
            fig_trend4.update_layout(title_y=0.95, title_x=0.5)

            plot_filename_trend4 = os.path.join(output_plot_dir, 'trend4_order_value_by_platform.html')
            fig_trend4.write_html(plot_filename_trend4)
            print(f"Trend 4 plot saved to {plot_filename_trend4}")
        else:
            print("Skipping Trend 4: Required columns ('Platform', 'Order Value (INR)') not found.")
    except Exception as e_trend4:
        print(f"Error investigating Trend 4: {repr(e_trend4)}")

    # --- Trend 5: Interaction between Platform and Product Category on Order Value ---
    # Error: UnicodeEncodeError caused by emoji in print statement.
    # Correction: Removed emoji.
    print("\n**Investigating Trend 5: Average Order Value by Category and Platform**")
    try:
        if 'Product Category' in df.columns and 'Platform' in df.columns and 'Order Value (INR)' in df.columns:
            # Ensure categorical columns are strings
            df['Product Category'] = df['Product Category'].astype(str)
            df['Platform'] = df['Platform'].astype(str)

            # Calculate average order value (px.bar does this automatically if y is numeric)
            fig_trend5 = px.bar(df,
                                x='Product Category',
                                y='Order Value (INR)',
                                color='Platform', # Group by platform
                                barmode='group', # Display bars side-by-side
                                title='Average Order Value by Category and Platform',
                                labels={'Order Value (INR)': 'Average Order Value (INR)', 'Product Category': 'Product Category', 'Platform': 'Platform'},
                                text_auto='.2s') # Display values on bars, formatted

            # Add interpretation guidance
            fig_trend5.add_annotation(text="<b>How to read:</b> Within each Product Category on the X-axis, compare the heights of the bars<br>"
                                          "representing different Platforms (indicated by color).<br>"
                                          "Identify categories where the average spending significantly differs based on the platform chosen.<br>"
                                          "Hover over bars for the specific average order value.",
                                      align='left',
                                      showarrow=False,
                                      xref='paper', yref='paper',
                                      x=0.02, y=0.98,
                                      bgcolor="rgba(255, 255, 255, 0.7)",
                                      bordercolor="black",
                                      borderwidth=1)
            fig_trend5.update_layout(title_y=0.95, title_x=0.5)
            fig_trend5.update_traces(textangle=0, textposition="outside") # Improve text readability

            plot_filename_trend5 = os.path.join(output_plot_dir, 'trend5_avg_value_category_platform.html')
            fig_trend5.write_html(plot_filename_trend5)
            print(f"Trend 5 plot saved to {plot_filename_trend5}")
        else:
            print("Skipping Trend 5: Required columns ('Product Category', 'Platform', 'Order Value (INR)') not found.")
    except Exception as e_trend5:
        print(f"Error investigating Trend 5: {repr(e_trend5)}")

    # --- Trend 6: Exploring High/Low Value Order Characteristics (Value vs Time, Colored by Rating) ---
    # Error: UnicodeEncodeError caused by emoji in print statement.
    # Correction: Removed emoji.
    print("\n**Investigating Trend 6: Order Value vs. Delivery Time, Colored by Service Rating**")
    try:
        if 'Delivery Time (Minutes)' in df.columns and 'Order Value (INR)' in df.columns and 'Service Rating' in df.columns:
            # Use a copy to ensure Service Rating is treated appropriately for color scale
            df_trend6 = df.copy()
            # Optional: Treat Service Rating as categorical for distinct colors, or keep numeric for gradient
            # df_trend6['Service Rating'] = df_trend6['Service Rating'].astype(str) # Uncomment for discrete colors

            fig_trend6 = px.scatter(df_trend6,
                                    x='Delivery Time (Minutes)',
                                    y='Order Value (INR)',
                                    color='Service Rating', # Color points by rating
                                    title='Order Value vs. Delivery Time, Colored by Service Rating',
                                    labels={'Delivery Time (Minutes)': 'Delivery Time (Minutes)',
                                            'Order Value (INR)': 'Order Value (INR)',
                                            'Service Rating': 'Service Rating'},
                                    hover_data=['Platform', 'Product Category']) # Add more info on hover

            # Add interpretation guidance
            fig_trend6.add_annotation(text="<b>How to read:</b> Each point is an order. X-axis = Delivery Time, Y-axis = Order Value, Color = Service Rating.<br>"
                                          "Observe the distribution of colors (ratings) across the plot.<br>"
                                          "- Are high-value orders (top) predominantly associated with high/low ratings (specific colors)?<br>"
                                          "- Are low-value orders (bottom) different?<br>"
                                          "- Is there a pattern related to delivery time (left=fast, right=slow)? E.g., do slow deliveries (right) have lower ratings (darker/specific colors)?<br>"
                                          "Hover over points for specific order details.",
                                      align='left',
                                      showarrow=False,
                                      xref='paper', yref='paper',
                                      x=0.02, y=0.98,
                                      bgcolor="rgba(255, 255, 255, 0.7)",
                                      bordercolor="black",
                                      borderwidth=1)
            fig_trend6.update_layout(title_y=0.95, title_x=0.5)

            plot_filename_trend6 = os.path.join(output_plot_dir, 'trend6_value_time_rating_scatter.html')
            fig_trend6.write_html(plot_filename_trend6)
            print(f"Trend 6 plot saved to {plot_filename_trend6}")
        else:
            print("Skipping Trend 6: Required columns ('Delivery Time (Minutes)', 'Order Value (INR)', 'Service Rating') not found.")
    except Exception as e_trend6:
        print(f"Error investigating Trend 6: {repr(e_trend6)}")

    # === End of Trend Investigation Steps ===

except FileNotFoundError:
    print(f"FATAL ERROR: Input file '{input_csv_path}' not found. Make sure the cleaning step ran successfully.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"FATAL ERROR: Input file '{input_csv_path}' is empty.")
    sys.exit(1)
except ImportError as e_imp:
    # Specific check for plotly which is critical
    if 'plotly' in str(e_imp).lower():
         print(f"FATAL ERROR: Plotly library not installed. Please install it using 'pip install plotly'. Error: {repr(e_imp)}.")
         sys.exit(1)
    else:
         print(f"FATAL ERROR: Required library not installed: {repr(e_imp)}.")
         sys.exit(1)
except Exception as e:
    # Error: Printing repr(e) could re-raise UnicodeEncodeError if the error message contains the problematic character.
    # Correction: Print a generic message and the type of the exception, or attempt to encode the error message safely.
    try:
        error_message = repr(e)
    except Exception: # Handle cases where repr(e) itself fails
        error_message = f"An error occurred, but its representation could not be displayed (Type: {type(e)})."
    # Attempt to encode the error message safely for printing
    try:
        safe_error_message = error_message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
    except Exception: # Fallback if encoding/decoding fails
        safe_error_message = f"An error occurred (Type: {type(e)}), but its details could not be safely encoded for printing."

    print(f"An unexpected error occurred during trend investigation setup or execution: {safe_error_message}")
    # Consider re-raising the exception for debugging if needed:
    # raise e
    sys.exit(1) # Exit on other major errors during setup or execution

print("\n**Finished Trends & Patterns Investigation Script**")
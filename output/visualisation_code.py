# Base structure - Implement the plan steps within this framework.
# Ensure all paths used are the absolute ones defined herein.
# You also need to explain to user how to understand or explore each plot, and this should be done on the plot or image itself.

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import re # Import re, listed in rules
import matplotlib.pyplot as plt # Also import matplotlib in case needed
import seaborn as sns # Import seaborn, listed in rules
import codecs # Import codecs for potential encoding issues, though removing chars is the primary fix

try:
    from tabulate import tabulate # Import tabulate if needed for tables
except ImportError:
    print("Warning: 'tabulate' library not found. Install it using 'pip install tabulate' if table printing is required.")
    # Define a dummy tabulate function if it's not critical
    def tabulate(data, headers='firstrow', tablefmt='psql', **kwargs):
        if headers == 'firstrow':
            header = data[0]
            data = data[1:]
        else:
            header = headers
        print("--- Table (tabulate not installed) ---")
        print("\t".join(map(str, header)))
        print("-" * (8 * len(header)))
        for row in data:
            print("\t".join(map(str, row)))
        print("--------------------------------------")
        return "Table printed in basic format."


# --- Define ABSOLUTE paths ---
input_csv_path = r'D:/AI Data Analysis/output/data_processed.csv' # Raw string literal
output_dir = r'D:/AI Data Analysis/output' # Base output directory
output_plot_dir = r'D:/AI Data Analysis/output/saved_plots' # Raw string literal for viz plots
output_trend_dir = r'D:/AI Data Analysis/output/trend_plots' # Raw string literal for trend plots

# Error: UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4ca'.
# Correction: Removed Unicode emojis from print statements for compatibility with non-UTF8 terminals (like default Windows console).
print("**Starting Data Visualization Script**")
print(f"Input cleaned file: {input_csv_path}")
print(f"Output plot directory: {output_plot_dir}")
print(f"Output trend directory: {output_trend_dir}") # Added print for trend dir

# --- Ensure plot directories exist ---
try:
    os.makedirs(output_plot_dir, exist_ok=True)
    print(f"Ensured plot directory exists: {output_plot_dir}")
    os.makedirs(output_trend_dir, exist_ok=True) # Added creation for trend dir
    print(f"Ensured trend directory exists: {output_trend_dir}")
except Exception as e:
    # Error: Could potentially fail if permissions are wrong.
    # Correction: Added specific try-except for directory creation.
    print(f"Error creating output directories {output_plot_dir} or {output_trend_dir}: {repr(e)}")
    # Decide if script should exit, maybe allow continuing if some plots fail
    sys.exit(1) # Exit if directories cannot be created, as saving will fail.

# --- Main script logic ---
try:
    # --- Read the input CSV (cleaned data) using absolute path ---
    # Error: FileNotFoundError or EmptyDataError could occur here.
    # Correction: Wrapped data loading in its own try-except block.
    try:
        df = pd.read_csv(input_csv_path)
        print(f"Successfully loaded {input_csv_path}. Shape: {df.shape}")
        if df.empty:
            print(f"Warning: Input file '{input_csv_path}' is empty. No plots will be generated.")
            sys.exit(0) # Exit gracefully if file is empty
    except FileNotFoundError:
        print(f"FATAL ERROR: Input file '{input_csv_path}' not found. Make sure the cleaning step ran successfully and the path is correct.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"FATAL ERROR: Input file '{input_csv_path}' is empty.")
        sys.exit(1)
    except Exception as e_read:
        print(f"FATAL ERROR reading CSV file {input_csv_path}: {repr(e_read)}")
        sys.exit(1)


    # === Implement Visualization Steps from Plan Here ===

    # 1. Distribution of Order Value (INR)
    # Error: UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4ca'.
    # Correction: Removed Unicode emoji from print statement.
    print("\n**[Plot 1] Generating: Distribution of Order Value (INR)**")
    try:
        plot_title1 = 'Distribution of Order Value (INR)'
        fig1 = px.histogram(df, x='Order Value (INR)', title=plot_title1,
                           labels={'Order Value (INR)': 'Order Value (INR)'})

        # Add interpretation guidance
        fig1.add_annotation(
            text="<b>Interpretation:</b> Hover over bars to see the count of orders within specific value ranges.<br>"
                 "Observe the shape to understand common order values and skewness (e.g., right-skewed means more lower-value orders).",
            align='left',
            showarrow=False,
            xref='paper', yref='paper',
            x=0.02, y=-0.15 # Position below x-axis
        )
        fig1.update_layout(margin=dict(b=100)) # Increase bottom margin for annotation

        # Construct absolute path for the plot file
        plot_filename1 = os.path.join(output_plot_dir, 'plot1_order_value_distribution.html')
        fig1.write_html(plot_filename1)
        print(f"Plot saved to {plot_filename1}")
    except KeyError as e_key:
        print(f"Error generating plot 1: KeyError - {repr(e_key)}. Column might be missing or misspelled.")
    except Exception as e_plot1:
        print(f"Error generating plot 1: {repr(e_plot1)}")

    # 2. Order Count per Platform
    # Error: UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4ca'.
    # Correction: Removed Unicode emoji from print statement.
    print("\n**[Plot 2] Generating: Order Count per Platform**")
    try:
        platform_counts = df['Platform'].value_counts().reset_index()
        platform_counts.columns = ['Platform', 'Count']
        plot_title2 = 'Total Number of Orders per Platform'
        fig2 = px.bar(platform_counts, x='Platform', y='Count', title=plot_title2,
                      labels={'Count': 'Number of Orders', 'Platform': 'Delivery Platform'},
                      text_auto=True) # Display count on bars

        # Add interpretation guidance
        fig2.add_annotation(
            text="<b>Interpretation:</b> Compare bar heights to identify the most popular platform(s) by order volume.<br>"
                 "Hover over bars for exact order counts per platform.",
            align='left',
            showarrow=False,
            xref='paper', yref='paper',
            x=0.02, y=-0.15 # Position below x-axis
        )
        fig2.update_layout(margin=dict(b=100)) # Increase bottom margin

        # Construct absolute path for the plot file
        plot_filename2 = os.path.join(output_plot_dir, 'plot2_platform_orders.html')
        fig2.write_html(plot_filename2)
        print(f"Plot saved to {plot_filename2}")
    except KeyError as e_key:
        print(f"Error generating plot 2: KeyError - {repr(e_key)}. Column 'Platform' might be missing.")
    except Exception as e_plot2:
        print(f"Error generating plot 2: {repr(e_plot2)}")

    # 3. Distribution of Delivery Time
    # Error: UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4c9'.
    # Correction: Removed Unicode emoji from print statement.
    print("\n**[Plot 3] Generating: Distribution of Delivery Time (Minutes)**")
    try:
        plot_title3 = 'Distribution of Delivery Time (Minutes)'
        fig3 = px.box(df, y='Delivery Time (Minutes)', title=plot_title3,
                      labels={'Delivery Time (Minutes)': 'Delivery Time (Minutes)'},
                      points='outliers') # Show outliers

        # Add interpretation guidance
        fig3.add_annotation(
            text="<b>Interpretation:</b> Observe the box plot elements:<br>"
                 "- Median (line inside box): Typical delivery time.<br>"
                 "- Box: Interquartile range (IQR), middle 50% of delivery times.<br>"
                 "- Whiskers: Range of typical data (often 1.5 * IQR).<br>"
                 "- Points beyond whiskers: Potential outliers (unusually long/short times).<br>"
                 "Hover over the box for Q1, Median, Q3 values.",
            align='left',
            showarrow=False,
            xref='paper', yref='paper',
            x=0.02, y=-0.20 # Position below x-axis, adjust y if needed
        )
        fig3.update_layout(margin=dict(b=120)) # Increase bottom margin

        # Construct absolute path for the plot file
        plot_filename3 = os.path.join(output_plot_dir, 'plot3_delivery_time_distribution.html')
        fig3.write_html(plot_filename3)
        print(f"Plot saved to {plot_filename3}")
    except KeyError as e_key:
        print(f"Error generating plot 3: KeyError - {repr(e_key)}. Column 'Delivery Time (Minutes)' might be missing.")
    except Exception as e_plot3:
        print(f"Error generating plot 3: {repr(e_plot3)}")

    # 4. Average Order Value by Product Category
    # Error: UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4ca'.
    # Correction: Removed Unicode emoji from print statement.
    print("\n**[Plot 4] Generating: Average Order Value (INR) by Product Category**")
    try:
        avg_value_category = df.groupby('Product Category')['Order Value (INR)'].mean().reset_index()
        avg_value_category = avg_value_category.sort_values('Order Value (INR)', ascending=False) # Sort for clarity
        plot_title4 = 'Average Order Value (INR) by Product Category'
        fig4 = px.bar(avg_value_category, x='Product Category', y='Order Value (INR)', title=plot_title4,
                      labels={'Order Value (INR)': 'Average Order Value (INR)', 'Product Category': 'Product Category'},
                      text_auto='.2f') # Display avg value on bars, formatted

        # Add interpretation guidance
        fig4.add_annotation(
            text="<b>Interpretation:</b> Compare bar heights to see which categories have the highest/lowest average order value.<br>"
                 "Hover over bars for specific average values. This helps identify high-value vs. low-value product groups.",
            align='left',
            showarrow=False,
            xref='paper', yref='paper',
            x=0.02, y=-0.15 # Position below x-axis
        )
        fig4.update_layout(margin=dict(b=100)) # Increase bottom margin

        # Construct absolute path for the plot file
        plot_filename4 = os.path.join(output_plot_dir, 'plot4_avg_value_per_category.html')
        fig4.write_html(plot_filename4)
        print(f"Plot saved to {plot_filename4}")
    except KeyError as e_key:
        print(f"Error generating plot 4: KeyError - {repr(e_key)}. Column 'Product Category' or 'Order Value (INR)' might be missing.")
    except Exception as e_plot4:
        print(f"Error generating plot 4: {repr(e_plot4)}")

    # 5. Distribution of Service Ratings
    # Error: UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4ca'.
    # Correction: Removed Unicode emoji from print statement.
    print("\n**[Plot 5] Generating: Distribution of Service Ratings (1-5)**")
    try:
        # Ensure ratings are treated as categories for distinct bars
        # Using bar on value_counts is often clearer for discrete ratings
        rating_counts = df['Service Rating'].value_counts().sort_index().reset_index()
        rating_counts.columns = ['Service Rating', 'Count']

        # Convert Service Rating to string/category if it's numeric to ensure discrete bars
        rating_counts['Service Rating'] = rating_counts['Service Rating'].astype(str)

        plot_title5 = 'Distribution of Service Ratings (1-5)'
        fig5 = px.bar(rating_counts, x='Service Rating', y='Count', title=plot_title5,
                      labels={'Count': 'Number of Orders', 'Service Rating': 'Service Rating (1-5)'},
                      text_auto=True) # Display count on bars
        fig5.update_xaxes(type='category') # Treat x-axis as categorical

        # Add interpretation guidance
        fig5.add_annotation(
            text="<b>Interpretation:</b> Observe the frequency (height of bars) for each rating score (1=Poor to 5=Excellent).<br>"
                 "Identify the most common ratings (customer satisfaction trends) and least common ratings.<br>"
                 "Hover over bars for exact counts.",
            align='left',
            showarrow=False,
            xref='paper', yref='paper',
            x=0.02, y=-0.15 # Position below x-axis
        )
        fig5.update_layout(margin=dict(b=100)) # Increase bottom margin

        # Construct absolute path for the plot file
        plot_filename5 = os.path.join(output_plot_dir, 'plot5_service_rating_distribution.html')
        fig5.write_html(plot_filename5)
        print(f"Plot saved to {plot_filename5}")
    except KeyError as e_key:
        print(f"Error generating plot 5: KeyError - {repr(e_key)}. Column 'Service Rating' might be missing.")
    except Exception as e_plot5:
        print(f"Error generating plot 5: {repr(e_plot5)}")

    # 6. Order Value vs. Delivery Time
    # Error: UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f4ca'.
    # Correction: Removed Unicode emoji from print statement.
    print("\n**[Plot 6] Generating: Order Value (INR) vs. Delivery Time (Minutes)**")
    try:
        plot_title6 = 'Order Value (INR) vs. Delivery Time (Minutes)'
        fig6 = px.scatter(df, x='Delivery Time (Minutes)', y='Order Value (INR)', title=plot_title6,
                          labels={'Delivery Time (Minutes)': 'Delivery Time (Minutes)', 'Order Value (INR)': 'Order Value (INR)'},
                          hover_data=['Platform', 'Product Category', 'Service Rating']) # Add more info on hover

        # Add interpretation guidance
        fig6.add_annotation(
            text="<b>Interpretation:</b> Each point represents an order. Look for patterns or trends:<br>"
                 "- Is there a correlation? (e.g., do higher value orders take longer/shorter?)<br>"
                 "- Are there clusters of points? (e.g., typical delivery times for certain order values?)<br>"
                 "Hover over points to see individual order details. Note the density of points in different areas.",
            align='left',
            showarrow=False,
            xref='paper', yref='paper',
            x=0.02, y=-0.15 # Position below x-axis
        )
        fig6.update_layout(margin=dict(b=120)) # Increase bottom margin

        # Construct absolute path for the plot file
        plot_filename6 = os.path.join(output_plot_dir, 'plot6_value_vs_delivery_time.html')
        fig6.write_html(plot_filename6)
        print(f"Plot saved to {plot_filename6}")
    except KeyError as e_key:
        print(f"Error generating plot 6: KeyError - {repr(e_key)}. Column 'Delivery Time (Minutes)' or 'Order Value (INR)' might be missing.")
    except Exception as e_plot6:
        print(f"Error generating plot 6: {repr(e_plot6)}")

    # === End of Visualization Steps ===

# Error: Catch specific library import errors if they are critical.
# Correction: Added specific check for Plotly import error.
except ImportError as e_imp:
    # Specific check for plotly which is critical
    if 'plotly' in str(e_imp).lower():
        print(f"FATAL ERROR: Plotly library not installed: {e_imp}. Please install it using 'pip install plotly'.")
        sys.exit(1)
    else:
        print(f"ImportError: A required library might be missing: {e_imp}.")
        # Decide if it's fatal or just a warning depending on the library
# Error: A broad exception might catch errors during setup before df is loaded, or other unexpected issues.
# Correction: Kept the broad except block at the end for truly unexpected errors.
except Exception as e:
    # Error: UnicodeEncodeError occurred here when printing the exception if the original error involved unicode.
    # Correction: The root cause (unicode in print statements) is fixed above. This block should now work.
    print(f"An unexpected error occurred during data visualization setup or execution: {repr(e)}")
    # raise e # Uncomment for debugging if needed, but avoid in production scripts that should report cleanly.
    sys.exit(1) # Exit with error code if an unexpected exception occurs

print("\n**Finished Data Visualization Script**")
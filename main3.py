import streamlit as st
import os
import pandas as pd
import numpy as np
import time
from pathlib import Path
import plotly.io as pio # Used for potentially validating html if needed, mainly for robust display
from aianalyst import run_agent  # Import LangGraph AI agent
from pathlib import Path

# --- Configuration ---
# Define standard file names and directories used/created by the agent
ORIGINAL_DATA_FILE = "data.csv"
PROCESSED_DATA_FILE = "output/data_processed.csv"
PLANS_FILES = {
    "Cleaning": "output/cleaning_plan.md",
    "Analysis": "output/analysis_plan.md",
    "Visualisation": "output/visualisation_plan.md",
    "Trends Plan": "output/trends_plan.md"
}
CODE_FILES = {
    "Cleaning": "output/cleaning_code.py",
    "Analysis": "output/analysis_code.py",
    "Visualisation": "output/visualisation_code.py",
    "Trends" : "output/trends_code.py"
    
}
OUTPUT_FILES = {
    "Analysis": "output/analysis_output.md"
}
PLOTS_DIR = Path("output/saved_plots") # Relative path
TRENDS_DIR = Path("output/trend_plots") # Relative path

# --- Helper Functions ---

def safe_read_file(file_path):
    """Safely reads text content from a file."""
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: File not found at `{file_path}`"
    except Exception as e:
        return f"Error reading file `{file_path}`: {str(e)}"

def display_csv_summary(tab, file_path, title):
    """Reads a CSV and displays a comprehensive summary in a Streamlit tab."""
    with tab:
        st.header(title)
        file = Path(file_path)
        if not file.is_file():
            st.warning(f"File not found: {file_path}. Please ensure the file exists.")
            # Optionally, try to provide more context based on the file path
            if file_path == PROCESSED_DATA_FILE:
                 st.info("This file is generated after running the AI Agent.")
            elif file_path == ORIGINAL_DATA_FILE:
                 st.info("Please upload a CSV file using the sidebar.")
            return # Stop execution for this tab if file not found

        try:
            df = pd.read_csv(file_path)

            st.subheader("📄 First 5 Rows")
            st.dataframe(df.head())

            st.subheader("📊 Column Information")
            st.dataframe(pd.DataFrame({
                "Data Type": df.dtypes,
                "Non-Null Count": df.count(),
                "Null Count": df.isnull().sum(),
                "Null Percentage (%)": (df.isnull().sum() / len(df) * 100).round(2)
            }))

            st.subheader("🔢 Statistical Summary (Numeric Columns)")
            numeric_cols = df.select_dtypes(include=np.number)
            if not numeric_cols.empty:
                st.dataframe(numeric_cols.describe().round(2))
            else:
                st.write("No numeric columns found for statistical summary.")

            st.subheader("📜 Statistical Summary (Object/Categorical Columns)")
            object_cols = df.select_dtypes(include=['object', 'category'])
            if not object_cols.empty:
                 st.dataframe(object_cols.describe())
            else:
                st.write("No object/categorical columns found for statistical summary.")

            st.subheader("❓ Missing Values ")
            # Simple text representation if missing values exist
            missing_values = df.isnull().sum()
            missing_cols = missing_values[missing_values > 0]
            if not missing_cols.empty:
                st.write("Columns with missing values:")
                st.dataframe(pd.DataFrame(missing_cols, columns=["Missing Count"]))
                # For a visual heatmap, consider using seaborn/matplotlib if heavy plotting is acceptable
                # Or create a simple Plotly heatmap if Plotly is a core dependency
            else:
                st.write("✅ No missing values detected.")


            st.subheader("🔗 Duplicate Rows")
            duplicates = df.duplicated().sum()
            st.write(f"Total Duplicate Rows: {duplicates} ({duplicates / len(df) * 100:.2f}%)")

            # Optional: Outliers (can be computationally intensive for large datasets)
            # Consider making this optional or showing only for key columns
            st.subheader("📈 Outliers Count (using IQR)")
            if not numeric_cols.empty:
                Q1 = numeric_cols.quantile(0.25)
                Q3 = numeric_cols.quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((numeric_cols < (Q1 - 1.5 * IQR)) | (numeric_cols > (Q3 + 1.5 * IQR))).sum()
                outliers_df = pd.DataFrame(outliers, columns=["Outliers Count"])
                outliers_df = outliers_df[outliers_df["Outliers Count"] > 0]
                if not outliers_df.empty:
                    st.dataframe(outliers_df)
                else:
                    st.write("No significant outliers detected using the IQR method.")
            else:
                st.write("No numeric columns to check for outliers.")


            st.subheader("✨ Unique Values in Categorical Columns (Sample)")
            if not object_cols.empty:
                unique_summary = {}
                for col in object_cols.columns:
                    unique_values = df[col].dropna().unique()
                    count = len(unique_values)
                    if count < 20: # Show values if fewer than 20 unique ones
                         unique_summary[col] = {'Count': count, 'Values': unique_values.tolist()}
                    else:
                         unique_summary[col] = {'Count': count, 'Values': unique_values[:10].tolist() + ['...']} # Show sample
                st.json(unique_summary, expanded=False)
            else:
                st.write("No categorical columns found.")


            st.subheader("↔️ Correlation Matrix (Numeric Columns)")
            if not numeric_cols.empty and len(numeric_cols.columns) > 1:
                corr_matrix = numeric_cols.corr().round(2)
                st.dataframe(corr_matrix)
                # Consider adding a heatmap here using st.plotly_chart or st.pyplot
            elif len(numeric_cols.columns) <= 1 :
                 st.write("Need at least two numeric columns to compute correlation.")
            else:
                st.write("No numeric columns found for correlation analysis.")

        except pd.errors.EmptyDataError:
            st.error(f"Error: The file '{file_path}' is empty.")
        except Exception as e:
            st.error(f"An error occurred while processing '{file_path}': {str(e)}")


def display_markdown_files(tab, files_dict):
    """Displays content from a dictionary of Markdown files in a tab."""
    with tab:
        st.header("📝 Agent Plans")
        for name, filepath in files_dict.items():
            st.subheader(f"{name} Plan")
            content = safe_read_file(filepath)
            if content.startswith("Error:"):
                st.warning(content)
            else:
                st.markdown(content, unsafe_allow_html=True) # Allow basic HTML if needed in MD

def display_code_files(tab, files_dict):
    """Displays content from a dictionary of Python code files in a tab."""
    with tab:
        st.header("🐍 Generated Code")
        for name, filepath in files_dict.items():
            st.subheader(f"{name} Code")
            content = safe_read_file(filepath)
            if content.startswith("Error:"):
                st.warning(content)
            else:
                st.code(content, language='python')

def display_markdown_outputs(tab, files_dict):
    """Displays content from a dictionary of Markdown output files in a tab."""
    with tab:
        st.header("📊 Analysis Outputs")
        for name, filepath in files_dict.items():
            st.subheader(f"{name} Output")
            contents = safe_read_file(filepath)
            # Ensure new lines are properly formatted
            #contents = content.replace("\n", "\n\n")  # Adds extra line breaks for Markdown rendering

            if contents.startswith("Error:"):
                st.warning(contents)
            else:
                st.code(contents, language="markdown")

# def display_plots(tab, title, plot_dir):
#     """Displays Plotly HTML plots found in a specified directory."""
#     with tab:
#         st.header(title)
#         if not plot_dir.is_dir():
#             st.warning(f"Plot directory not found: `{plot_dir}`. Run the agent to generate plots.")
#             return

#         html_files = sorted(list(plot_dir.glob("*.html")))

#         if not html_files:
#             st.info(f"No `.html` plots found in `{plot_dir}`.")
#             return

#         for i, file_path in enumerate(html_files):
#             st.subheader(f"Plot: {file_path.name}")
#             try:
#                 # It's generally safer to read as bytes first, then decode
#                 html_content_bytes = file_path.read_bytes()
#                 html_content = html_content_bytes.decode("utf-8", errors="replace") # Replace invalid chars
                
#                 # Use unique key for each component
#                 st.components.v1.html(html_content, height=500, scrolling=True) 
                
#             except Exception as e:
#                 st.error(f"Error displaying plot `{file_path.name}`: {str(e)}")
def display_plots(tab, title, plot_dir):
    """Displays various plot types found in a specified directory (HTML, PNG, JPG, etc.)."""
    with tab:
        st.header(title)

        if not plot_dir.is_dir():
            st.warning(f"Plot directory not found: `{plot_dir}`. Run the agent to generate plots.")
            return

        # Supported plot types
        html_files = sorted(plot_dir.glob("*.html"))  # Plotly
        image_files = sorted(plot_dir.glob("*.png")) + sorted(plot_dir.glob("*.jpg"))  # Matplotlib, Seaborn

        if not html_files and not image_files:
            st.info(f"No supported plots (`.html`, `.png`, `.jpg`) found in `{plot_dir}`.")
            return

        # Display Plotly HTML files
        for file_path in html_files:
            st.subheader(f"Plot: {file_path.stem}")  # Removes .html, .png, .jpg, etc.

            try:
                html_content_bytes = file_path.read_bytes()
                html_content = html_content_bytes.decode("utf-8", errors="replace")
                st.components.v1.html(html_content, height=500, scrolling=True)
            except Exception as e:
                st.error(f"Error displaying Plotly plot `{file_path.name}`: {str(e)}")

        # Display Matplotlib / Seaborn images
        for file_path in image_files:
            st.subheader(f"Plot: {file_path.stem}")  # Removes .html, .png, .jpg, etc.

            try:
                image = Image.open(file_path)
                st.image(image, use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image `{file_path.name}`: {str(e)}")


# --- Streamlit App Layout ---

st.set_page_config(page_title="AI Data Analysis Agent", layout="wide")

# Initialize session state
if 'agent_run_complete' not in st.session_state:
    st.session_state.agent_run_complete = False
if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = False

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Controls")

    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], key="file_uploader")

    if uploaded_file is not None:
        # Save the uploaded file to the designated original data file path
        try:
            with open(ORIGINAL_DATA_FILE, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"File '{uploaded_file.name}' uploaded and saved as `{ORIGINAL_DATA_FILE}`.")
            st.session_state.data_uploaded = True
            # Reset agent run status if new data is uploaded
            st.session_state.agent_run_complete = False
        except Exception as e:
            st.error(f"Error saving uploaded file: {e}")
            st.session_state.data_uploaded = False
    elif Path(ORIGINAL_DATA_FILE).exists():
        # If file exists from previous session but wasn't uploaded now
        st.session_state.data_uploaded = True
        # Keep existing agent_run_complete status

    st.header("2. Run AI Agent")
    st.info("The agent will process the uploaded data, generate plans, code, analysis, and visualizations.")

    # Only enable the button if data has been uploaded
    run_button_disabled = not st.session_state.data_uploaded
    if st.button("🚀 Run AI Agent", disabled=run_button_disabled, type="primary"):
        # --- Import and Run Agent ---
        # We import here to avoid potential issues if aiagent has heavy imports
        # and the user hasn't uploaded a file yet.
        try:
            from aianalyst import run_agent
        except ImportError:
            st.error("Fatal Error: Could not import `run_agent` from `aiagent.py`. Ensure the file exists and is configured correctly.")
            st.stop() # Stop execution if agent can't be imported

        # Ensure output directories exist before running the agent
        # The agent *should* ideally create them, but this is a safety measure
        try:
            PLOTS_DIR.mkdir(parents=True, exist_ok=True)
            TRENDS_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
             st.warning(f"Could not create output directories: {e}. The agent might fail if it cannot write files.")

        with st.spinner("🤖 AI Agent is analyzing the data... Please wait."):
            try:
                # --- Execute the LangGraph AI agent ---
                run_agent()
                # --- Agent execution finished ---

                # Verify expected output files (optional but recommended)
                if Path(PROCESSED_DATA_FILE).is_file():
                    st.session_state.agent_run_complete = True
                    st.success("✅ AI Agent finished successfully!")
                    # Use st.experimental_rerun() if you *really* need to force a full refresh
                    # but session state should handle updates correctly now.
                    # st.experimental_rerun()
                else:
                    st.error(f"Agent run seemed to complete, but the processed data file (`{PROCESSED_DATA_FILE}`) was not found. Please check agent logs.")
                    st.session_state.agent_run_complete = False

            except Exception as e:
                st.error(f"An error occurred during AI agent execution: {str(e)}")
                st.exception(e) # Shows traceback for debugging
                st.session_state.agent_run_complete = False

    if run_button_disabled:
        st.warning("Please upload a CSV file first to enable the AI Agent.")


# --- Main Area Tabs ---
st.title("📊 AI Data Analysis Report")

tab_titles = [
    "📄 Original Data",
    "✨ Processed Data",
    "📝 Plans",
    "🐍 Code",
    "💡 Outputs",
    "📈 Visualizations",
    "📉 Trends"
]
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(tab_titles)

# Tab 1: Original Data Summary
display_csv_summary(tab1, ORIGINAL_DATA_FILE, "Original Data Summary")

# Tabs 2-7: Display results only if the agent has run successfully
if st.session_state.get('agent_run_complete', False):
    display_csv_summary(tab2, PROCESSED_DATA_FILE, "Processed Data Summary")
    display_markdown_files(tab3, PLANS_FILES)
    display_code_files(tab4, CODE_FILES)
    display_markdown_outputs(tab5, OUTPUT_FILES)
    display_plots(tab6, "📊 Generated Visualizations", PLOTS_DIR)
    display_plots(tab7, "📉 Trend Analysis Plots", TRENDS_DIR)
else:
    # Show placeholders in tabs 2-7 if agent hasn't run
    tabs_to_inform = [tab2, tab3, tab4, tab5, tab6, tab7]
    for tab in tabs_to_inform:
        with tab:
            st.info("Run the AI Agent from the sidebar to generate content for this tab.")


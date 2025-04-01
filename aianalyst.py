import os
import re
import subprocess
import sys
import tempfile
from typing import TypedDict, Annotated, Dict, Any

# Third-party imports
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
# Removed: from langchain_experimental.utilities import PythonREPL
from langgraph.graph import END, StateGraph

# Potentially used by generated code, keep for now unless confirmed unnecessary
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd # Often needed by generated code
import plotly.express as px # Often needed by generated code
import plotly.graph_objects as go # Often needed by generated code
from tabulate import tabulate # Often needed by generated code


# --- Configuration ---
# Set your Gemini API Key here or as an environment variable
# os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY" # Replace with your key if needed
# Using the key provided in the original code
GEMINI_MODEL_NAME = "gemini-2.5-pro-exp-03-25" # Use a stable, available Pro model like 1.5 Pro

# --- Initialize Python REPL Tool (REPLACED with Subprocess Execution) ---
# Removed: repl = PythonREPL()


@tool
def execute_python_code(code: Annotated[str, "Python code to execute using subprocess"]):
    """
    Executes Python code using a separate subprocess and returns the
    standard output and standard error.
    Ensure code includes print() statements for visibility of results.
    Handles imports and multi-line script execution by writing to a temporary file.
    """
    print("--- Preparing Subprocess Execution ---")
    # Clean the code first (remove markdown fences if present)
    cleaned_code = clean_code(code)
    if not cleaned_code:
        error_message = "Execution Error: No valid Python code provided to execute."
        print(error_message)
        return error_message

    # Create a temporary file to store the code
    # Using delete=False so we control deletion after subprocess potentially errors
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tf:
            tf.write(cleaned_code)
            temp_file_path = tf.name
        print(f"Code written to temporary file: {temp_file_path}")

        # Execute the temporary file using the same Python interpreter that runs this script
        # This helps ensure library availability matches the parent environment
        process = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            encoding='utf-8', # Ensure consistent encoding
            timeout=300  # Add a timeout (e.g., 5 minutes)
        )

        print("--- Subprocess Execution Output ---")
        print("STDOUT:")
        print(process.stdout if process.stdout else "<No stdout>")
        print("STDERR:")
        print(process.stderr if process.stderr else "<No stderr>")
        print(f"Return Code: {process.returncode}")
        print("--- End Subprocess Output ---")

        if process.returncode == 0:
            # Success
            output = process.stdout if process.stdout else "No output."
            # Add a marker for success, similar to the original REPL tool
            return f"Execution successful. Output:\n{output}"
        else:
            # Failure
            error_output = process.stderr if process.stderr else "No error message captured."
            error_message = f"Execution Error: Subprocess failed with return code {process.returncode}. Error:\n{error_output}"
            return error_message

    except subprocess.TimeoutExpired:
        error_message = f"Execution Error: Code execution timed out after 300 seconds."
        print(error_message)
        return error_message
    except Exception as e:
        # Catch exceptions during file creation, subprocess execution setup, etc.
        error_message = f"Execution Error: Failed to execute code via subprocess. Error: {repr(e)}"
        print(error_message)
        return error_message
    finally:
        # Clean up the temporary file if it was created
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"Temporary file deleted: {temp_file_path}")
            except Exception as e_del:
                print(f"Warning: Could not delete temporary file {temp_file_path}: {e_del}")


# --- Helper Functions --- (Unchanged)

def read_code_from_file(file_path: str) -> str:
    """Reads code from a specified file."""
    try:
        # Ensure the path uses forward slashes for consistency, especially if mixing OS
        file_path = file_path.replace("\\", "/")
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: File not found at {file_path}. Returning empty string.")
        return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def write_content_to_file(file_path: str, content: str, wrap_in_markdown: bool = False):
    """Writes content to a specified file, optionally wrapping in markdown."""
    try:
        # Ensure the path uses forward slashes for consistency
        file_path = file_path.replace("\\", "/")
        # Ensure directory exists
        dir_name = os.path.dirname(file_path)
        if dir_name: # Ensure dirname is not empty (happens if filename is in current dir)
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            if wrap_in_markdown:
                file.write(f"```\n{content}\n```") # Standard markdown block
            else:
                file.write(content)
        print(f"Successfully wrote content to {file_path}")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")

def clean_code(code: str) -> str:
    """Removes markdown code fences and language identifiers."""
    if not isinstance(code, str):
        print("Warning: clean_code received non-string input. Returning empty string.")
        return ""
    # Remove markdown fences and optional language identifiers (python, py, etc.)
    # Handles potential whitespace variations and multi-line correctly
    cleaned = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", code, flags=re.MULTILINE | re.DOTALL).strip()
    return cleaned

# --- Initialize LLM --- (Unchanged)
# Using the hardcoded API key from the environment variable set above
model = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL_NAME,
    api_key="", # Use env var
    temperature=0.3,
    # max_tokens=10000, # Adjust based on model limits if needed, 1.5 Pro has larger context
    convert_system_message_to_human=True # Often improves compatibility with Gemini
    # safety_settings=... # Optional: configure safety settings if needed
)

# Bind the NEW execute_python_code tool to the model
model_with_tools = model.bind_tools([execute_python_code])

# --- Agent State Definition --- (Unchanged)
class AgentState(TypedDict):
    initial_script_path: str       # HARDCODED Absolute Path to the initial python script
    cleaned_script_path: str     # HARDCODED Absolute Path to the script for summarizing cleaned data
    input_csv_path: str          # HARDCODED Absolute Path to the input CSV (changes after cleaning)
    output_dir: str              # HARDCODED Absolute Path Directory for saving outputs

    current_code: str            # Code currently being worked on
    code_description: str        # Description of the current code's purpose

    # Planning outputs
    cleaning_plan: str
    analysis_plan: str
    visualisation_plan: str
    trends_plan: str

    # Execution outputs and errors
    tool_output: str             # Raw output from the last tool execution
    execution_error: bool        # Flag indicating if the last execution failed
    error_message: str           # Specific error message from execution or debugging

    # Control Flow & Counters
    iterations: int              # General iteration count
    rewrite_attempts: int        # Counts attempts to rewrite the *current* failing script
    max_rewrite_attempts: int    # Maximum allowed rewrites per script
    current_step: str            # Tracks the major step
    stop_execution: bool         # Flag to signal the end of the workflow

    # File Naming
    current_output_filename: str # Base name for the output file (code or markdown log)

    # Conversational Interaction Fields (Kept for structure, but unused)
    current_plan_type: str
    current_plan_content: str
    user_confirmation: str
    user_feedback: str

    # Added for explicit context passing
    cleaned_summary_content: str # To store the summary after cleaning

# --- Agent Nodes ---

def initialize_state(state: AgentState): # (Unchanged)
    """Initializes the agent's state with hardcoded absolute paths."""
    print("--- Initializing State ---")
    state['iterations'] = 0
    state['max_rewrite_attempts'] = 4

    # --- HARDCODED ABSOLUTE PATHS ---
    state['initial_script_path'] = "D:/AI Data Analysis/datanew.py"
    state['cleaned_script_path'] = "D:/AI Data Analysis/datanewcleaned.py"
    state['input_csv_path'] = "D:/AI Data Analysis/data.csv"
    state['output_dir'] = "D:/AI Data Analysis/output"
    # --- END HARDCODED PATHS ---

    # Ensure paths use forward slashes internally for consistency
    state['initial_script_path'] = state['initial_script_path'].replace("\\", "/")
    state['cleaned_script_path'] = state['cleaned_script_path'].replace("\\", "/")
    state['input_csv_path'] = state['input_csv_path'].replace("\\", "/")
    state['output_dir'] = state['output_dir'].replace("\\", "/")

    # Initial step setup
    state['current_step'] = "initial_summary"
    state['code_description'] = "Generate initial data summary"
    state['current_code'] = read_code_from_file(state['initial_script_path'])
    # Output filename relative to output_dir
    state['current_output_filename'] = "initial_summary_output.md"

    # Reset execution state
    state['tool_output'] = ""
    state['execution_error'] = False
    state['error_message'] = ""
    state['rewrite_attempts'] = 0
    state['stop_execution'] = False

    # Reset conversational state (unused)
    state['current_plan_type'] = ""
    state['current_plan_content'] = ""
    state['user_confirmation'] = ""
    state['user_feedback'] = ""

    # Reset plans and summaries
    state['cleaning_plan'] = ""
    state['analysis_plan'] = ""
    state['visualisation_plan'] = ""
    state['trends_plan'] = ""
    state['cleaned_summary_content'] = ""

    # Ensure output directory exists (using the absolute path)
    try:
        os.makedirs(state['output_dir'], exist_ok=True)
    except Exception as e:
        print(f"ERROR: Could not create output directory {state['output_dir']}: {e}")
        state['stop_execution'] = True
        return state

    # Check if initial script exists
    if not state['current_code']:
        print(f"ERROR: Initial script not found or empty at {state['initial_script_path']}. Stopping.")
        state['stop_execution'] = True

    print(f"State Initialized. Starting Step: {state['current_step']}")
    print(f"Input CSV: {state['input_csv_path']}")
    print(f"Output Directory: {state['output_dir']}")
    return state


def execute_code(state: AgentState):
    """
    Executes the code currently in state['current_code'] by invoking the LLM
    to use the 'execute_python_code' tool (which now uses subprocess).
    """
    state['iterations'] += 1
    state['rewrite_attempts'] = 0 # Reset rewrite attempts when starting execution
    print(f"""
--- Executing Code: {state['code_description']} (Iteration: {state['iterations']}) ---""")
    print(f"Input CSV Path Context for Execution: {state['input_csv_path']}")
    print(f"Output Directory Context for Execution: {state['output_dir']}")

    # Use the code directly from the state
    code_to_execute = state['current_code']
    if not code_to_execute:
        print("Error: No code found in state to execute.")
        state['execution_error'] = True
        state['error_message'] = "No code provided for execution."
        state['tool_output'] = state['error_message']
        return state

    # No need to clean here, clean_code is called inside the tool now
    print("--- Code to Execute (via Subprocess Tool) ---")
    print(code_to_execute)
    print("--- End Code ---")


    # Prepare messages for the model to use the tool
    messages = [
        SystemMessage(
            content=f"""Your task is to execute the given Python code using the 'execute_python_code' tool.
The code aims to perform: {state['code_description']}.
The code should use the following *absolute* paths already embedded within it:
- Input CSV: '{state['input_csv_path']}'
- Output Directory Base: '{state['output_dir']}' (for saving files like cleaned data, plots, etc.)

Execute the code exactly as provided. Do not modify it. Call the 'execute_python_code' tool with the code.
The code expects necessary libraries like pandas, plotly, os, re, matplotlib, seaborn, tabulate to be available in the execution environment.
The code might generate output files (CSV, plots). These should be saved within the '{state['output_dir']}' directory or its subdirectories based on paths *inside the code itself*.
"""
        ),
        HumanMessage(content=f'Use the execute_python_code tool to execute this Python Code:\n```python\n{code_to_execute}\n```'),
    ]

    try:
        # Invoke the model, expecting it to call the tool
        ai_msg = model_with_tools.invoke(messages)
        state['tool_output'] = "" # Reset tool output

        if not ai_msg.tool_calls:
            print("Error: Model did not return a tool call.")
            state['execution_error'] = True
            state['error_message'] = "Model failed to invoke the execute_python_code tool."
            state['tool_output'] = state['error_message']
            return state

        # Process tool calls (expecting one for execute_python_code)
        tool_invoked = False
        for tool_call in ai_msg.tool_calls:
            if tool_call["name"].lower() == "execute_python_code":
                print(f"Tool call received: {tool_call['name']}")
                # The tool itself executes the code string via subprocess
                # tool_call["args"]["code"] should contain the code string
                tool_output = execute_python_code.invoke(tool_call["args"]) # No need to pass code explicitly, it's in args
                state['tool_output'] = str(tool_output) # Store raw output
                messages.append(ai_msg) # Add AI message before ToolMessage
                messages.append(ToolMessage(content=state['tool_output'], tool_call_id=tool_call["id"]))
                tool_invoked = True
                break # Assuming only one call needed
            else:
                print(f"Warning: Unexpected tool call requested: {tool_call['name']}")

        if not tool_invoked:
            print("Error: Model called a tool, but not the expected 'execute_python_code' tool.")
            state['execution_error'] = True
            state['error_message'] = "Model invoked an unexpected tool."
            state['tool_output'] = f"Model invoked tool '{ai_msg.tool_calls[0]['name']}' instead of 'execute_python_code'."
            return state

    except Exception as e:
        print(f"Error invoking model or tool: {repr(e)}")
        state['execution_error'] = True
        state['error_message'] = f"LLM or Tool Invocation Error: {repr(e)}"
        state['tool_output'] = state['error_message']
        return state

    # --- Process Execution Result ---
    print(f"Raw Tool Output Received (first 1000 chars): {state['tool_output'][:1000]}...")

    # Check for errors based on the prefix added by the execute_python_code tool
    if state['tool_output'].strip().startswith("Execution Error:"):
        state['execution_error'] = True
        # Extract the error message after the prefix
        state['error_message'] = state['tool_output'][len("Execution Error:"):].strip()
        print(f"Execution Error Detected via Prefix: {state['error_message']}")
    # Consider any output containing common error keywords as potential failure (less reliable than prefix)
    elif any(keyword in state['tool_output'][:3000].lower() for keyword in ["error", "exception", "failed", "traceback"]):
        state['execution_error'] = True
        state['error_message'] = f"Potential error detected based on keywords in output. Full output: {state['tool_output']}"
        print(f"Potential Execution Error Detected via Keywords.")
    else:
        state['execution_error'] = False
        state['error_message'] = ""
        print("Execution Successful.")
        # Save successful output log to the designated file
        if state.get('output_dir') and state.get('current_output_filename'):
            # Construct absolute path for the log file
            output_file_path = os.path.join(state['output_dir'], state['current_output_filename']).replace("\\", "/")
            # Save the *full* tool output (which now includes the "Execution successful. Output:\n" prefix)
            write_content_to_file(output_file_path, state['tool_output'], wrap_in_markdown=False)
        else:
            print("Warning: Could not save execution output log - output directory or filename missing in state.")

        # Special handling after successful steps that produce summaries
        if state['current_step'] == "execute_cleaned_summary":
            print("Storing cleaned data summary content.")
            # Store the relevant part of the output (excluding the success prefix)
            summary_start = "Execution successful. Output:\n"
            if state['tool_output'].startswith(summary_start):
                state['cleaned_summary_content'] = state['tool_output'][len(summary_start):].strip()
            else:
                 state['cleaned_summary_content'] = state['tool_output'] # Store raw if prefix missing


    return state


def rewrite_code_on_error(state: AgentState): # (Unchanged in logic, but context from subprocess stderr is different)
    """Attempts to rewrite the code based on the execution error message."""
    state['rewrite_attempts'] += 1
    print(f"""
--- Rewriting Code: {state['code_description']} (Attempt: {state['rewrite_attempts']}/{state['max_rewrite_attempts']}) ---""")

    code_to_fix = state['current_code']
    error = state['error_message'] # This now comes from subprocess stderr via the tool output

    # Truncate error message if too long for the prompt
    max_error_length = 2000 # Increase slightly for potentially more verbose stderr
    if len(error) > max_error_length:
        error = error[:max_error_length] + "... (truncated)"

    print(f"Error Message (from subprocess): {error}")

    # Determine the correct paths to emphasize based on the code description
    current_input_csv = state['input_csv_path']
    base_output_dir = state['output_dir']
    cleaned_csv_filename = "data_processed.csv" # Relative filename
    cleaned_csv_path_abs = os.path.join(base_output_dir, cleaned_csv_filename).replace("\\", "/")
    plot_dir_abs = os.path.join(base_output_dir, 'saved_plots').replace("\\", "/")
    trend_plot_dir_abs = os.path.join(base_output_dir, 'trend_plots').replace("\\", "/")


    debug_instructions = ""
    if "visualisation" in state['code_description'].lower() or "trends" in state['code_description'].lower():
        plot_save_dir = trend_plot_dir_abs if "trends" in state['code_description'].lower() else plot_dir_abs
        debug_instructions = f"""
    **Visualization/Plotting Specific Instructions:**
    - Ensure plots are saved to the correct *absolute* directory: '{plot_save_dir}'. Use `os.makedirs('{plot_save_dir}', exist_ok=True)` before saving.
    - Ensure plots are saved correctly (e.g., `fig.write_html(os.path.join('{plot_save_dir}', 'filename.html'))` for plotly, `plt.savefig(os.path.join('{plot_save_dir}', 'filename.png'))` for matplotlib).
    - If a plot fails due to complexity or unclear errors, comment out the failing section with explanation (`# Removed Plot X due to error: <error message>`). Wrap plotting calls in try-except blocks.
    - Check data preparation steps (type conversion, NaNs) before plotting. Use try-except blocks around individual plotting sections.
    - Ensure all necessary plotting libraries (plotly.express, plotly.graph_objects, matplotlib.pyplot) are imported.
    """
    elif "cleaning" in state['code_description'].lower():
        debug_instructions = f"""
    **Data Cleaning Specific Instructions:**
    - Ensure the input CSV is read from the correct *absolute* path: '{current_input_csv}'.
    - Ensure the final cleaned data is saved correctly to the *absolute* path: '{cleaned_csv_path_abs}'.
    - Pay close attention to data types (`astype()`) and missing values (`fillna()`, `dropna()`). Check pandas operations carefully. Wrap steps in try-except.
    - Ensure `os` is imported if `os.path` or `os.makedirs` is used.
    """
    elif "analysis" in state['code_description'].lower():
        debug_instructions = f"""
    **Data Analysis Specific Instructions:**
    - Ensure the input CSV (cleaned data) is read from the correct *absolute* path: '{current_input_csv}'. (Note: this should be the path to the cleaned data, usually '{cleaned_csv_path_abs}')
    - Ensure `tabulate` is imported and used correctly for printing DataFrames (use `.head(10)` if large).
    - Check pandas operations (`groupby`, `value_counts`, aggregations). Use try-except blocks around individual analysis sections.
    """

    messages = [
        SystemMessage(
            content=f"""You are an expert Python debugger for data analysis scripts that run in a standard Python environment.
Analyze the given Python code and the error message (likely from stderr). Correct the code and return **only the complete, corrected Python script**.

**Code Description:** {state['code_description']}
**Input CSV ABSOLUTE Path (Expected in Code):** '{current_input_csv}'
**Output Directory ABSOLUTE Path (Expected in Code):** '{base_output_dir}'
(Cleaned data should go to '{cleaned_csv_path_abs}')
(Viz plots to '{plot_dir_abs}')
(Trend plots to '{trend_plot_dir_abs}')

**Debugging Rules:**
*   Ensure all paths used for reading/writing files are **ABSOLUTE** paths as specified above and used correctly (e.g., using `r'...'` or forward slashes). Use `os.path.join()` correctly.
*   Use `os.makedirs(..., exist_ok=True)` *before* attempting to save files into directories like plot dirs. Ensure `os` is imported.
*   Ensure necessary libraries (pandas, plotly.*, os, re, matplotlib, seaborn, tabulate, sys) are imported. Check for `ImportError` or `ModuleNotFoundError` in the error message.
*   Add detailed `try-except Exception as e:` blocks around individual file operations, analysis steps, or plotting sections to catch errors locally and print informative messages (`print(f"Error in section X: {{repr(e)}}")`). This helps pinpoint failures.
*   Address the specific error reported in the error message: `{error}`
*   If a section seems fundamentally unfixable based on the error, comment it out clearly: `# Error: [description]. Correction: Commented out failing section due to unresolvable error.`
*   Add comments explaining significant fixes: `# Error: <original issue>. Correction: <what you did>.`
*   Maintain the original purpose of the code.
{debug_instructions}

**Output Format:**
- Return **ONLY** the complete, corrected Python code.
- **NO markdown fences** (like ```python ... ```).
- **NO explanations** outside the code comments.
- The code must be immediately executable. Start with `import ...`.
"""
        ),
        HumanMessage(content=f"**Original Code:**\n```python\n{code_to_fix}\n```\n\n**Error Message (from stderr/subprocess):**\n{error}\n\n**Correct the code:**"),
    ]

    try:
        ai_msg = model.invoke(messages)
        corrected_code = clean_code(ai_msg.content) # Clean potential markdown fences

        if corrected_code and corrected_code != clean_code(code_to_fix): # Check if code was generated and changed
            print("--- Rewritten Code ---")
            print(corrected_code)
            state['current_code'] = corrected_code
            state['execution_error'] = False # Assume fixed, will be checked on next execution
            state['error_message'] = ""

            # Save the rewritten code back to its corresponding generated file in the output dir
            original_filename = None
            # Determine filename based on the *step that failed*
            failed_step_for_filename = state['current_step'] # The step that led to the error
            if failed_step_for_filename == "execute_cleaning":
                original_filename = "cleaning_code.py"
            elif failed_step_for_filename == "execute_analysis":
                original_filename = "analysis_code.py"
            elif failed_step_for_filename == "execute_visualisation":
                original_filename = "visualisation_code.py"
            elif failed_step_for_filename == "execute_trends":
                original_filename = "trends_code.py"
            # Add cases if initial or cleaned summary scripts can be rewritten (currently they are read-only)
            elif failed_step_for_filename == "initial_summary":
                 # Decide if we allow rewriting the initial script file D:/.../datanew.py
                 # For safety, let's only rewrite generated files in output/
                 print("Skipping rewrite save for initial_summary script.")
                 pass
            elif failed_step_for_filename == "execute_cleaned_summary":
                 # Decide if we allow rewriting the cleaned summary script file D:/.../datanewcleaned.py
                 # For safety, let's only rewrite generated files in output/
                 print("Skipping rewrite save for cleaned_summary script.")
                 pass


            if original_filename:
                # Construct absolute path for the code file within the output directory
                output_code_path = os.path.join(state['output_dir'], original_filename).replace("\\", "/")
                write_content_to_file(output_code_path, corrected_code, wrap_in_markdown=False)
                print(f"Saved corrected code to {output_code_path}")
            else:
                print(f"Warning: Could not determine output filename to save rewritten code for step '{failed_step_for_filename}'.")


        elif corrected_code:
            print("Info: Model returned the same code. No changes made.")
            # Consider stopping if the model can't fix it after attempts? For now, rely on max_rewrite_attempts check.
        else:
            print("ERROR: Model failed to generate corrected code.")
            # Keep the old code and error state, proceed to check rewrite limit

    except Exception as e:
        print(f"Error during code rewrite invocation: {repr(e)}")
        # Keep the old code and error state, proceed to check rewrite limit

    return state


# --- Planning and Code Generation Nodes --- (Unchanged in logic, prompts adapted for absolute paths)

def generate_plan(state: AgentState, plan_type: str): # (Unchanged)
    """Generates a plan (cleaning, analysis, viz, trends) based on the last tool output / summary."""
    print(f"""
--- Generating {plan_type.capitalize()} Plan ---""")

    # Determine which summary content to use
    summary_content = ""
    summary_source = ""
    if plan_type == "cleaning":
        # Use output from initial summary execution (extract from tool_output)
        raw_output = state.get('tool_output', '')
        summary_start = "Execution successful. Output:\n"
        if raw_output.startswith(summary_start):
             summary_content = raw_output[len(summary_start):].strip()
        else:
             summary_content = raw_output # Use raw if prefix missing or it was an error message
        summary_source = "Initial Data Summary"
    else:
        # For analysis, viz, trends, use the summary of the *cleaned* data
        summary_content = state.get('cleaned_summary_content', '')
        summary_source = "Cleaned Data Summary"
        if not summary_content:
            # Fallback if cleaned summary somehow wasn't stored or cleaning failed
            summary_content = state.get('tool_output', '') # Could be cleaning output or error
            summary_source = "Previous Step Output (Fallback)"

    if not summary_content:
        print(f"Warning: No {summary_source} found to generate {plan_type} plan. Attempting generic plan.")
        summary_content = "No dataset summary was provided. Please generate a generic plan based on common data analysis tasks."

    # Hardcoded paths for context in prompts
    # Use the initial state paths for clarity in the plan description
    initial_csv_abs = "D:/AI Data Analysis/data.csv".replace("\\", "/") # Explicit hardcode based on initialize
    output_dir_abs = state['output_dir'] # Absolute
    cleaned_csv_abs = os.path.join(output_dir_abs, "data_processed.csv").replace("\\", "/")
    plot_dir_abs = os.path.join(output_dir_abs, 'saved_plots').replace("\\", "/")
    trend_plot_dir_abs = os.path.join(output_dir_abs, 'trend_plots').replace("\\", "/")

    plan_prompts = {
        "cleaning": {
            "system": f"""You are a meticulous Data Analyst creating a **detailed, step-by-step data cleaning plan** based on the provided summary of an uncleaned dataset. The goal is to prepare the data for analysis and visualization.

**Dataset Context (Absolute Paths):**
- Initial Uncleaned Data Path (Input for code): '{initial_csv_abs}'
- Output Cleaned Data Path (Target for code): '{cleaned_csv_abs}'

**Based on the provided summary:**
1.  **Datatypes:** Identify columns with incorrect types and specify the correct one (e.g., convert 'Date' from object to datetime).
2.  **Missing Values:** Propose a specific strategy for each column (e.g., fill 'Age' with median, drop rows missing 'OrderID'). Justify briefly.
3.  **Duplicates:** Specify how to handle duplicate rows (e.g., drop exact duplicates).
4.  **Outliers:** Identify potential outliers (based on stats if available). Decide *if* and *how* to handle (e.g., cap 'Salary' at 99th percentile, or state 'No outlier treatment needed').
5.  **Consistency/Formatting:** Suggest fixes for inconsistent text (e.g., standardize 'Country', trim whitespace).
6.  **Minimal Feature Engineering:** Suggest simple combinations if obvious (e.g., 'FirstName' + 'LastName' -> 'FullName').

**Formatting Requirements:**
- Output **only the plan** in markdown format. Use emojis (🧹, ✨), bold text, and numbered/bullet points.
- Example: `🧹 **1. Handle Missing Values**\n - Fill `Age` with median (Rationale: Skewed distribution maybe).`
- **Do NOT include Python code snippets.**
- **Do NOT use '#' for Markdown headings.** Use numbered lists or bold text.
- Mention column names explicitly.
""",
            "human": f"**{summary_source}:**\n```\n{summary_content}\n```\n\n**Generate the Data Cleaning Plan:**",
            "output_field": "cleaning_plan",
            "output_filename": "cleaning_plan.md" # Relative to output_dir
        },
        "analysis": {
            "system": f"""You are an insightful Data Analyst generating **up to 10 actionable analysis questions/steps** for a Python script, based on a summary of a **cleaned** dataset.

**Dataset Context (Absolute Paths):**
- Cleaned Data Path (Input for code): '{cleaned_csv_abs}'

**Analysis Goals:** Reveal insights, patterns, relationships using pandas (aggregation, filtering, value_counts, correlations).
- You also need to explain to user how to understand or make sense of each analysis.

**Output Handling Guidance (for the *code* to be generated later):**
*   Plan for concise output. If results are large (>10-15 rows), print a summary, use grouping, or print only `.head(10)`.
*   Code should use `print()` with bold markdown (`print("\\n**📊 Analysis: [Question]**")`).
*   Code should use `tabulate` for formatted tables (`.head(10)` before tabulating if large). Ensure `tabulate` is imported.

**Formatting Requirements (for this Plan):**
- Output **only the analysis questions/steps** in markdown. Use emojis (❓, 💡, 📈), bold text, numbered lists.
- Example: `❓ **1. What is the distribution of [Column]?**\n - Calculate value counts, display top 10 using tabulate.`
- **Maximum 10 questions.**
- **No Python code implementation.**
- Do not suggest visualizations or data cleaning.
""",
            "human": f"**{summary_source}:**\n```\n{summary_content}\n```\n\n**Generate the Data Analysis Plan:**",
            "output_field": "analysis_plan",
            "output_filename": "analysis_plan.md" # Relative to output_dir
        },
        "visualisation": {
            "system": f"""You are a Data Visualization Expert proposing a blueprint for **up to 6 impactful visualizations** using Plotly, based on a summary of a **cleaned** dataset.

**Dataset Context (Absolute Paths):**
- Cleaned Data Path (Input for code): '{cleaned_csv_abs}'
- Plot Output Directory (Target for code): '{plot_dir_abs}'

**Visualization Goals:** Illustrate key insights, relationships, distributions. Choose appropriate Plotly types (histogram, bar, scatter, line, boxplot).
- You also need to explain to user how to understand or explore each plot, and this should be done on the plot or image itself.

**Guidance for the Plan:**
- Suggest specific columns and plot types.
- Include simple aggregations if needed (e.g., "Bar chart of average Salary per Department").
- Specify a meaningful title and output filename (e.g., `plot1_distribution.html`) for each plot. Code should save plots as HTML in the specified absolute plot directory. Code must use `os.makedirs('{plot_dir_abs}', exist_ok=True)`.
**Formatting Requirements (for this Plan):**
- Output **only the visualization blueprint** in markdown. Use emojis (📈, 📊, 📉), bold text, numbered lists.
- Example: `📈 **1. Distribution of Age**\n - Create histogram of `Age` using `plotly.express.histogram`. Title: 'Distribution of Age'. Save as `plot1_age_distribution.html` in '{os.path.basename(plot_dir_abs)}/'.`
- **Maximum 6 plots.**
- **No Python code implementation.**
- Do not suggest data cleaning or non-visualization analysis.
""",
            "human": f"**{summary_source}:**\n```\n{summary_content}\n```\n\n**Generate the Visualization Plan:**",
            "output_field": "visualisation_plan",
            "output_filename": "visualisation_plan.md" # Relative to output_dir
        },
        "trends": {
            "system": f"""You are a Data Scientist identifying **up to 6 potential key trends or patterns** requiring further investigation with Plotly, based on a **cleaned** dataset summary and a list of already planned visualizations. Aim for insights *not* obviously covered by the planned basic plots.

**Dataset Context (Absolute Paths):**
- Cleaned Data Path (Input for code): '{cleaned_csv_abs}'
- Trend Plot Output Directory (Target for code): '{trend_plot_dir_abs}'

**Trend Identification Goals:** Look for time trends, multi-variable correlations, segment-specific behaviors, anomalies. Suggest specific Plotly visualizations or analyses (e.g., rolling average, heatmap, scatter matrix).
- You also need to explain to user how to understand or explore each plot, and this should be done on the plot or image itself.

**Guidance for the Plan:**
- Suggest specific columns, analysis/plot type, title, and output filename (e.g., `trend1_correlation_heatmap.html`). Code should save plots as HTML. Code must use `os.makedirs('{trend_plot_dir_abs}', exist_ok=True)`.
- **Crucially: Do not simply repeat visualizations listed in the 'Already Planned Visualizations' section.** Focus on *different* or *deeper* insights.

**Formatting Requirements (for this Plan):**
- Output **only the trends/patterns blueprint** in markdown. Use emojis (🔍, ✨, 🧭), bold text, numbered lists.
- Example: `🔍 **1. Explore Correlation between Feature A and B**\n - Generate scatter plot with trendline using `plotly.express.scatter`. Title: 'Trend between A and B'. Save as `trend1_A_vs_B.html` in '{os.path.basename(trend_plot_dir_abs)}/'.`
- **Maximum 6 trends/plots.**
- **No Python code implementation.**
- Do not suggest data cleaning.
""",
            "human": f"**{summary_source}:**\n```\n{summary_content}\n```\n\n**Already Planned Visualizations (Do NOT repeat):**\n{state.get('visualisation_plan', 'None')}\n\n**Generate the Trends & Patterns Plan:**",
            "output_field": "trends_plan",
            "output_filename": "trends_plan.md" # Relative to output_dir
                }
        }

    prompt_config = plan_prompts.get(plan_type)
    if not prompt_config:
        print(f"Error: Invalid plan type '{plan_type}'.")
        state['stop_execution'] = True
        return state

    messages = [
        SystemMessage(content=prompt_config["system"]),
        HumanMessage(content=prompt_config["human"])
    ]

    try:
        ai_msg = model.invoke(messages)
        plan_content = ai_msg.content
        state[prompt_config["output_field"]] = plan_content

        print(f"--- Generated {plan_type.capitalize()} Plan (Preview) ---")
        print(plan_content[:1000] + "..." if len(plan_content) > 1000 else plan_content)

        # Save the generated plan to the output directory (absolute path)
        output_file_path = os.path.join(state['output_dir'], prompt_config["output_filename"]).replace("\\", "/")
        write_content_to_file(output_file_path, plan_content, wrap_in_markdown=False) # Plan is already markdown

    except Exception as e:
        print(f"Error generating {plan_type} plan: {repr(e)}")
        state['error_message'] = f"Failed to generate {plan_type} plan: {repr(e)}"
        state['stop_execution'] = True # Stop if planning fails

    # Reset unused user interaction fields
    state['user_confirmation'] = ""
    state['user_feedback'] = ""

    return state


def generate_code_from_plan(state: AgentState, plan_type: str): # (Unchanged in logic, prompts adapted)
    """Generates Python code based on a previously generated plan, using hardcoded absolute paths."""
    print(f"""
--- Generating Code for: {plan_type.capitalize()} ---""")

    # Define absolute paths based on current state for use in generated code
    base_output_dir = state['output_dir'] # Absolute
    # Determine which input CSV path the code should use based on the plan type
    if plan_type == "cleaning":
        # Use the *initial* CSV path from the state
        current_input_csv = "D:/AI Data Analysis/data.csv".replace("\\", "/") # Explicit hardcode based on initialize
    else:
        # Analysis, Viz, Trends use the *current* input_csv_path from the state,
        # which should point to the cleaned data after the cleaning step runs.
        current_input_csv = state['input_csv_path'] # Absolute path to cleaned data

    cleaned_csv_abs = os.path.join(base_output_dir, "data_processed.csv").replace("\\", "/")
    plot_dir_abs = os.path.join(base_output_dir, 'saved_plots').replace("\\", "/")
    trend_plot_dir_abs = os.path.join(base_output_dir, 'trend_plots').replace("\\", "/")


    # Define plan details including base code templates with placeholders for absolute paths
    plan_details_config = {
        "cleaning": {
            "plan_field": "cleaning_plan",
            "code_description": "Data cleaning script based on plan",
            "output_filename": "cleaning_code.py", # Relative to output_dir
            "extra_instructions_template": """
import pandas as pd
import os
import re # Include re just in case needed
import sys # For potential path manipulation if needed, though absolute used

# --- Define ABSOLUTE paths to use ---
input_path = r'{input_path_placeholder}' # Raw string literal for Windows paths
output_cleaned_path = r'{output_csv_placeholder}' # Raw string literal
output_dir_base = os.path.dirname(output_cleaned_path)

print(f"**Starting Data Cleaning Script**")
print(f"Input file: {{input_path}}")
print(f"Output file: {{output_cleaned_path}}")

# --- Ensure output directory exists ---
try:
    os.makedirs(output_dir_base, exist_ok=True)
    print(f"Ensured output directory exists: {{output_dir_base}}")
except Exception as e:
    print(f"Error creating output directory {{output_dir_base}}: {{repr(e)}}")
    # Consider sys.exit(1) if directory creation is critical

try:
    # --- Read the input CSV using the absolute path ---
    df = pd.read_csv(input_path)
    print(f"Successfully loaded {{input_path}}. Initial Shape: {{df.shape}}")

    # === Implement Cleaning Steps from Plan Here ===
    # (LLM inserts code based on the cleaning plan)
    # Example:
    # print("\\n--- Applying Cleaning Step: Handling Missing Values ---")
    # try:
    #     # df['Age'].fillna(df['Age'].median(), inplace=True)
    #     # print("Filled missing 'Age' values with median.")
    # except KeyError as e_key:
    #     print(f"KeyError during cleaning step 'Age': {{repr(e_key)}} - Column might be missing.")
    # except Exception as e_clean_step1:
    #     print(f"Error during cleaning step 'Age': {{repr(e_clean_step1)}}")
    # === End of Cleaning Steps ===

    # --- Save the cleaned data to the absolute output path ---
    df.to_csv(output_cleaned_path, index=False, encoding='utf-8') # Specify encoding
    print(f"\\n**🧹 Cleaned data saved successfully to {{output_cleaned_path}}**")
    print(f"Cleaned data shape: {{df.shape}}")

except FileNotFoundError:
    print(f"FATAL ERROR: Input file '{{input_path}}' not found.")
    sys.exit(1) # Exit if input file not found
except pd.errors.EmptyDataError:
    print(f"FATAL ERROR: Input file '{{input_path}}' is empty.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during data cleaning: {{repr(e)}}")
    # Optional: re-raise the exception if debugging is needed
    # raise e

print("**Finished Data Cleaning Script**")
"""
        },
        "analysis": {
            "plan_field": "analysis_plan",
            "code_description": "Data analysis script based on plan",
            "output_filename": "analysis_code.py", # Relative to output_dir
            "extra_instructions_template": """ You also need to explain to user how to understand or make sense of each analysis.
import pandas as pd
import os
import sys
try:
    from tabulate import tabulate # Make sure tabulate is available
except ImportError:
    print("Error: 'tabulate' library not found. Please install it (`pip install tabulate`).")
    # Fallback print function if tabulate is missing
    def tabulate(data, headers, tablefmt, showindex):
        print(headers)
        for row in data.values.tolist(): print(row)


# --- Define ABSOLUTE path for input cleaned data ---
input_csv_path = r'{input_path_placeholder}' # Raw string literal

# --- Set pandas display options ---
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 100) # Show more rows if needed

print("**Starting Data Analysis Script**")
print(f"Input cleaned file: {{input_csv_path}}")

try:
    # --- Read the input CSV (cleaned data) using absolute path ---
    df = pd.read_csv(input_csv_path)
    print(f"Successfully loaded {{input_csv_path}}. Shape: {{df.shape}}")

    # === Implement Analysis Steps from Plan Here ===
    # (LLM inserts code based on the analysis plan)
    # Example using try-except per step:
    # print("\\n**❓ Analysis: [Question 1 from plan]**")
    # try:
    #   result1 = df.groupby('some_column').size().reset_index(name='count').sort_values('count', ascending=False)
    #   print(f"Analysis Result for Question 1 (Top 10):")
    #   if not result1.empty:
    #       print(tabulate(result1.head(10), headers='keys', tablefmt='psql', showindex=False))
    #   else:
    #       print("No results found for this analysis.")
    # except KeyError as e_key:
    #    print(f"KeyError during analysis step 1: {{repr(e_key)}} - Column might be missing or mistyped.")
    # except Exception as e_step1:
    #   print(f"Error during analysis step 1: {{repr(e_step1)}}")
    # === End of Analysis Steps ===

except FileNotFoundError:
    print(f"FATAL ERROR: Input file '{{input_csv_path}}' not found. Make sure the cleaning step ran successfully and saved the file correctly.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"FATAL ERROR: Input file '{{input_csv_path}}' is empty.")
    sys.exit(1)
except ImportError as e_imp: # Catch specific import error for tabulate maybe
    print(f"FATAL ERROR: Required library not installed: {{e_imp}}. Cannot proceed with analysis.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during data analysis setup or execution: {{repr(e)}}")
    # raise e

print("\\n**Finished Data Analysis Script**")
"""
        },
        "visualisation": {
            "plan_field": "visualisation_plan",
            "code_description": "Data visualization script based on plan",
            "output_filename": "visualisation_code.py", # Relative to output_dir
            "extra_instructions_template": """ You also need to explain to user how to understand or explore each plot, and this should be done on the plot or image itself.

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import matplotlib.pyplot as plt # Also import matplotlib in case needed

# --- Define ABSOLUTE paths ---
input_csv_path = r'{input_path_placeholder}' # Raw string literal
output_plot_dir = r'{output_plot_dir_placeholder}' # Raw string literal

print("**Starting Data Visualization Script**")
print(f"Input cleaned file: {{input_csv_path}}")
print(f"Output plot directory: {{output_plot_dir}}")

# --- Ensure plot directory exists ---
try:
    os.makedirs(output_plot_dir, exist_ok=True)
    print(f"Ensured plot directory exists: {{output_plot_dir}}")
except Exception as e:
    print(f"Error creating plot directory {{output_plot_dir}}: {{repr(e)}}")
    # Decide if script should exit, maybe allow continuing if some plots fail

try:
    # --- Read the input CSV (cleaned data) using absolute path ---
    df = pd.read_csv(input_csv_path)
    print(f"Successfully loaded {{input_csv_path}}. Shape: {{df.shape}}")

    # === Implement Visualization Steps from Plan Here ===
    # (LLM inserts code based on the visualization plan)
    # Example using try-except per plot:
    # print("\\n**📊 Generating: [Plot 1 description from plan]**")
    # try:
    #     fig1 = px.histogram(df, x='Age', title='Distribution of Age')
    #     # Construct absolute path for the plot file
    #     plot_filename1 = os.path.join(output_plot_dir, 'plot1_age_distribution.html')
    #     fig1.write_html(plot_filename1)
    #     print(f"Plot saved to {{plot_filename1}}")
    # except KeyError as e_key:
    #     print(f"KeyError generating plot 1: {{repr(e_key)}} - Column 'Age' might be missing.")
    # except Exception as e_plot1:
    #     print(f"Error generating plot 1: {{repr(e_plot1)}}")
    # === End of Visualization Steps ===

except FileNotFoundError:
    print(f"FATAL ERROR: Input file '{{input_csv_path}}' not found. Make sure the cleaning step ran successfully.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"FATAL ERROR: Input file '{{input_csv_path}}' is empty.")
    sys.exit(1)
except ImportError as e_imp:
    print(f"FATAL ERROR: Required library (e.g., plotly) not installed: {{e_imp}}.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during data visualization setup or execution: {{repr(e)}}")
    # raise e

print("\\n**Finished Data Visualization Script**")
"""
        },
        "trends": {
            "plan_field": "trends_plan",
            "code_description": "Trends and patterns identification script based on plan",
            "output_filename": "trends_code.py", # R elative to output_dir
            "extra_instructions_template": """ You also need to explain to user how to understand or explore each plot, and this should be done on the plot or image itself. 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import matplotlib.pyplot as plt # Also import matplotlib in case needed

# --- Define ABSOLUTE paths ---
input_csv_path = r'{input_path_placeholder}' # Raw string literal
output_plot_dir = r'{output_plot_dir_placeholder}' # Trend plots directory (Raw string literal)

print("**Starting Trends & Patterns Investigation Script**")
print(f"Input cleaned file: {{input_csv_path}}")
print(f"Output trend plot directory: {{output_plot_dir}}")

# --- Ensure trend plot directory exists ---
try:
    os.makedirs(output_plot_dir, exist_ok=True)
    print(f"Ensured trend plot directory exists: {{output_plot_dir}}")
except Exception as e:
    print(f"Error creating trend plot directory {{output_plot_dir}}: {{repr(e)}}")
    # Decide if script should exit

try:
    # --- Read the input CSV (cleaned data) using absolute path ---
    df = pd.read_csv(input_csv_path)
    print(f"Successfully loaded {{input_csv_path}}. Shape: {{df.shape}}")

    # === Implement Trend Investigation Steps from Plan Here ===
    # (LLM inserts code based on the trends plan)
    # Example using try-except per trend:
    # print("\\n**🔍 Investigating Trend: [Trend 1 description from plan]**")
    # try:
    #     # Example: Correlation heatmap
    #     numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    #     if len(numeric_cols) > 1:
    #         corr = df[numeric_cols].corr()
    #         fig_trend1 = px.imshow(corr, text_auto=True, aspect="auto", title='Correlation Heatmap')
    #         plot_filename_trend1 = os.path.join(output_plot_dir, 'trend1_correlation_heatmap.html')
    #         fig_trend1.write_html(plot_filename_trend1)
    #         print(f"Trend plot saved to {{plot_filename_trend1}}")
    #     else:
    #         print("Skipping correlation heatmap: Not enough numeric columns found.")
    # except Exception as e_trend1:
    #     print(f"Error investigating trend 1 (Correlation): {{repr(e_trend1)}}")
    # === End of Trend Investigation Steps ===

except FileNotFoundError:
    print(f"FATAL ERROR: Input file '{{input_csv_path}}' not found. Make sure the cleaning step ran successfully.")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"FATAL ERROR: Input file '{{input_csv_path}}' is empty.")
    sys.exit(1)
except ImportError as e_imp:
    print(f"FATAL ERROR: Required library (e.g., plotly) not installed: {{e_imp}}.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during trend investigation setup or execution: {{repr(e)}}")
    # raise e

print("\\n**Finished Trends & Patterns Investigation Script**")
"""
            }
        }


    config = plan_details_config.get(plan_type)
    if not config:
        print(f"Error: Invalid plan type '{plan_type}' for code generation.")
        state['stop_execution'] = True
        return state

    plan = state.get(config["plan_field"])
    if not plan:
        print(f"Error: {plan_type.capitalize()} plan not found in state (field: {config['plan_field']}). Cannot generate code.")
        state['stop_execution'] = True
        return state

    # Format the extra_instructions template with the correct absolute paths
    if plan_type == "cleaning":
        formatted_instructions = config["extra_instructions_template"].format(
            input_path_placeholder=current_input_csv, # Should be the initial CSV path
            output_csv_placeholder=cleaned_csv_abs
        )
    elif plan_type == "analysis":
        formatted_instructions = config["extra_instructions_template"].format(
            input_path_placeholder=current_input_csv # Should be the cleaned CSV path
        )
    elif plan_type == "visualisation":
        formatted_instructions = config["extra_instructions_template"].format(
            input_path_placeholder=current_input_csv, # Should be the cleaned CSV path
            output_plot_dir_placeholder=plot_dir_abs
        )
    elif plan_type == "trends":
        formatted_instructions = config["extra_instructions_template"].format(
            input_path_placeholder=current_input_csv, # Should be the cleaned CSV path
            output_plot_dir_placeholder=trend_plot_dir_abs
        )
    else:
        # Should not happen due to earlier check, but handle defensively
        print(f"Error: Unknown plan type '{plan_type}' during instruction formatting.")
        state['stop_execution'] = True
        return state


    # Construct the final prompt for code generation
    messages = [
        SystemMessage(
            content=f"""You are an expert Python Developer for data tasks using pandas and Plotly.
You will be given a plan ({config['code_description']}) and need to write a complete, executable Python script to implement it.

**CRITICAL INSTRUCTIONS:**
*   The script MUST use the **ABSOLUTE paths** provided within the base script structure below for all file operations (reading CSVs, saving CSVs, saving plots). Use raw string literals (e.g., `r'D:/path/to/file.csv'`) or forward slashes for paths.
*   Import necessary standard libraries: `pandas`, `os`, `sys`, `re`.
*   Import required plotting/output libraries: `plotly.express as px`, `plotly.graph_objects as go`, `matplotlib.pyplot as plt`, `from tabulate import tabulate`. Wrap `tabulate` import in try-except if needed.
*   Implement each step from the provided plan within the designated sections ('=== Implement ... Steps from Plan Here ===') of the base structure.
*   Use robust `try-except Exception as e:` blocks for file I/O and individual analysis/plotting steps. Print informative error messages if exceptions occur (`print(f"Error in section X: {{repr(e)}}")`). Use `sys.exit(1)` after printing FATAL errors (like file not found).
*   Ensure directories for output (plots, cleaned data) are created using `os.makedirs(..., exist_ok=True)` *before* writing files to them.
*   Follow output requirements from the plan (e.g., saving plots to correct absolute paths as HTML, using `print()` with markdown formatting for analysis steps, using `tabulate` with `.head(10)` for large tables).

**Base Script Structure (Use this template and fill in the implementation):**
```python
# Base structure - Implement the plan steps within this framework.
# Ensure all paths used are the absolute ones defined herein.
{formatted_instructions}
```

**OUTPUT REQUIREMENT:**
- Return **ONLY** the complete Python script implementing the plan using the structure above.
- **NO markdown fences** (```python ... ```).
- **NO explanations** outside the Python code comments.
- Start directly with `import pandas as pd`.
"""
        ),
        HumanMessage(content=f"**Plan to Implement:**\n```markdown\n{plan}\n```\n\n**Generate the Python code:**")
    ]

    try:
        ai_msg = model.invoke(messages)
        generated_code = clean_code(ai_msg.content)

        if not generated_code:
            raise ValueError("Model failed to generate code.")

        print(f"--- Generated Code ({plan_type}) ---")
        print(generated_code[:1500] + "..." if len(generated_code) > 1500 else generated_code)

        state['current_code'] = generated_code
        state['code_description'] = config['code_description']
        # Set filename for saving the *execution log* (relative to output_dir)
        state['current_output_filename'] = config['output_filename'].replace('.py', '_output.md')

        # IMPORTANT: Update input_csv_path in the state for subsequent steps IF this is the cleaning step
        if plan_type == "cleaning":
            # The *next* step (cleaned summary, analysis, etc.) will use the cleaned CSV path.
            state['input_csv_path'] = cleaned_csv_abs # Update state with the absolute path
            print(f"Input CSV path for next steps updated to (absolute): {state['input_csv_path']}")

        # Save the generated code script itself to the output directory (absolute path)
        output_code_path = os.path.join(state['output_dir'], config['output_filename']).replace("\\", "/")
        write_content_to_file(output_code_path, generated_code, wrap_in_markdown=False)
        print(f"Generated code saved to: {output_code_path}")

    except Exception as e:
        print(f"Error generating code for {plan_type}: {repr(e)}")
        state['error_message'] = f"Failed to generate code for {plan_type}: {repr(e)}"
        state['stop_execution'] = True

    return state


# --- Node Wrappers for Planning and Code Generation --- (Unchanged)

def plan_cleaning(state: AgentState):
    """Generates the cleaning plan."""
    state = generate_plan(state, "cleaning")
    # Transition handled by graph edge
    return state

def generate_cleaning_code(state: AgentState):
    """Generates code based on the cleaning plan."""
    state = generate_code_from_plan(state, "cleaning")
    state['current_step'] = "execute_cleaning"
    # Log filename is relative here, joined with output_dir later
    state['current_output_filename'] = "cleaning_execution_log.md"
    return state

def load_cleaned_summary_script(state: AgentState):
    """Loads the script to summarize the *cleaned* data."""
    print("""
--- Loading Script for Cleaned Data Summary ---""")
    state['current_step'] = "execute_cleaned_summary"
    script_path = state['cleaned_script_path'] # Absolute path from init
    state['current_code'] = read_code_from_file(script_path)
    state['code_description'] = "Generate summary of cleaned data"
    # input_csv_path should now point to the cleaned data absolute path (updated after cleaning execution)
    print(f"Using input CSV for cleaned summary (absolute): {state['input_csv_path']}")
    # Log filename is relative
    state['current_output_filename'] = "cleaned_summary_output.md"

    if not state['current_code']:
        print(f"ERROR: Cleaned summary script not found or empty at {script_path}. Stopping.")
        state['error_message'] = f"Script not found: {script_path}"
        state['stop_execution'] = True
    return state

def plan_analysis(state: AgentState):
    """Generates the analysis plan using the cleaned summary."""
    # Ensure cleaned summary is available (should be in state['cleaned_summary_content'])
    if not state.get('cleaned_summary_content'):
        print("Warning: Cleaned summary content not found in state for analysis planning.")
        # generate_plan has fallback logic, but good to note here.
    state = generate_plan(state, "analysis")
    return state

def generate_analysis_code(state: AgentState):
    """Generates code based on the analysis plan."""
    state = generate_code_from_plan(state, "analysis")
    state['current_step'] = "execute_analysis"
    state['current_output_filename'] = "analysis_output.md" # Log filename relative
    return state

def plan_visualisation(state: AgentState):
    """Generates the visualization plan using the cleaned summary."""
    if not state.get('cleaned_summary_content'):
        print("Warning: Cleaned summary content not found in state for visualization planning.")
    state = generate_plan(state, "visualisation")
    return state

def generate_visualisation_code(state: AgentState):
    """Generates code based on the visualization plan."""
    state = generate_code_from_plan(state, "visualisation")
    state['current_step'] = "execute_visualisation"
    state['current_output_filename'] = "visualisation_log.md" # Log filename relative
    return state

def plan_trends(state: AgentState):
    """Generates the trends plan using cleaned summary and viz plan."""
    if not state.get('cleaned_summary_content'):
        print("Warning: Cleaned summary content not found in state for trends planning.")
    if not state.get('visualisation_plan'):
        print("Warning: Visualization plan not found in state for trends planning context.")
    state = generate_plan(state, "trends")
    return state

def generate_trends_code(state: AgentState):
    """Generates code based on the trends plan."""
    state = generate_code_from_plan(state, "trends")
    state['current_step'] = "execute_trends"
    state['current_output_filename'] = "trends_log.md" # Log filename relative
    return state

# --- Conditional Edges --- (Unchanged)

def route_after_execution(state: AgentState):
    """Determines the next step after code execution based on success/error and current step."""
    print(f"""
--- Routing after Execution ({state['current_step']}) ---""")
    if state.get('stop_execution', False):
        print("Stop signal received. Ending workflow.")
        return END

    if state.get('execution_error', False):
        print(f"Execution failed. Error: {state.get('error_message', 'Unknown error')[:300]}...")
        if state.get('rewrite_attempts', 0) < state.get('max_rewrite_attempts', 4):
            print(f"Attempting rewrite (Attempt {state['rewrite_attempts']+1}/{state['max_rewrite_attempts']}).")
            return "rewrite_code"
        else:
            print(f"Max rewrite attempts ({state.get('max_rewrite_attempts', 4)}) reached for step {state['current_step']}. Stopping.")
            state['stop_execution'] = True
            return END
    else:
        print("Execution successful.")
        # Transition based on the step that just completed successfully
        current_step = state.get('current_step')
        if current_step == "initial_summary":
            return "plan_cleaning"
        elif current_step == "execute_cleaning":
            # After cleaning code runs, load the script to summarize the cleaned data
            return "load_cleaned_summary_script"
        elif current_step == "execute_cleaned_summary":
            # After cleaned summary is generated, plan the main analysis
            return "plan_analysis"
        elif current_step == "execute_analysis":
            # After analysis code runs, plan visualizations
            return "plan_visualisation"
        elif current_step == "execute_visualisation":
            # After visualization code runs, plan trends
            return "plan_trends"
        elif current_step == "execute_trends":
            # Final step's code completed successfully
            print("All steps completed successfully. Ending workflow.")
            return END
        else:
            print(f"Warning: Unknown current_step '{current_step}' after successful execution. Attempting to end.")
            return END


# --- Build the Graph --- (Unchanged structure, nodes remain the same)

workflow = StateGraph(AgentState)

# Add Core Nodes
workflow.add_node("initialize_state", initialize_state)
workflow.add_node("execute_code", execute_code) # This node now uses the new tool internally
workflow.add_node("rewrite_code", rewrite_code_on_error)

# Add Planning Nodes
workflow.add_node("plan_cleaning", plan_cleaning)
workflow.add_node("plan_analysis", plan_analysis)
workflow.add_node("plan_visualisation", plan_visualisation)
workflow.add_node("plan_trends", plan_trends)

# Add Code Generation Nodes
workflow.add_node("generate_cleaning_code", generate_cleaning_code)
workflow.add_node("generate_analysis_code", generate_analysis_code)
workflow.add_node("generate_visualisation_code", generate_visualisation_code)
workflow.add_node("generate_trends_code", generate_trends_code)

# Special node to load the script for summarizing cleaned data
workflow.add_node("load_cleaned_summary_script", load_cleaned_summary_script)


# --- Define Edges --- (Unchanged)

# Entry Point
workflow.set_entry_point("initialize_state")

# Initial Summary Flow: Initialize -> Execute Initial Script
workflow.add_edge("initialize_state", "execute_code")

# Routing after any code execution (initial, cleaning, cleaned_summary, analysis, viz, trends)
workflow.add_conditional_edges(
    "execute_code",
    route_after_execution,
    {
        "rewrite_code": "rewrite_code",          # If execution failed and retries remain
        "plan_cleaning": "plan_cleaning",          # Success: After initial summary
        "load_cleaned_summary_script": "load_cleaned_summary_script", # Success: After cleaning code
        "plan_analysis": "plan_analysis",          # Success: After cleaned summary script
        "plan_visualisation": "plan_visualisation",    # Success: After analysis code
        "plan_trends": "plan_trends",              # Success: After visualisation code
        END: END                                 # If error limit reached, final success, or unknown state
    }
)

# Loop back after rewrite attempt -> Execute again
workflow.add_edge("rewrite_code", "execute_code")

# After Planning -> Go directly to Code Generation
workflow.add_edge("plan_cleaning", "generate_cleaning_code")
workflow.add_edge("plan_analysis", "generate_analysis_code")
workflow.add_edge("plan_visualisation", "generate_visualisation_code")
workflow.add_edge("plan_trends", "generate_trends_code")

# After Code Generation -> Go to Execute the generated code
workflow.add_edge("generate_cleaning_code", "execute_code")
workflow.add_edge("generate_analysis_code", "execute_code")
workflow.add_edge("generate_visualisation_code", "execute_code")
workflow.add_edge("generate_trends_code", "execute_code")

# After loading cleaned summary script -> Execute it
workflow.add_edge("load_cleaned_summary_script", "execute_code")


# Compile the graph
app = workflow.compile()

# --- Run the Workflow ---
# if __name__ == "__main__":
#     print("\n" + "="*50)
#     print(" Starting AI Data Analyst Workflow (using Subprocess) ")
#     print("="*50 + "\n")

#     # Define the initial state dictionary (although initialize_state sets most)
#     initial_state = {}

#     # Stream the execution
#     try:
#         for event in app.stream(initial_state):
#             # Print event information (which node is running, the output)
#             for node_name, output in event.items():
#                 print(f"--- Event: Node '{node_name}' ---")
#                 # print(f"Output:\n{output}") # Can be very verbose, print selectively if needed
#                 print("-" * (len(node_name) + 14)) # Separator
#             print("\n") # Add space between events
#     except Exception as e:
#         print(f"\n\n!!! Workflow Execution Failed !!!")
#         print(f"Error: {repr(e)}")
#         import traceback
#         print("Traceback:")
#         traceback.print_exc()

#     print("\n" + "="*50)
#     print(" AI Data Analyst Workflow Finished ")
#     print("="*50 + "\n")
#     print(f"Check the '{os.path.abspath('D:/AI Data Analyst Rough/output')}' directory for generated plans, code, logs, and plots.")

def run_agent():
    """Invokes the LangGraph agent."""
    print("Starting Agent Workflow...")
    # We don't need to pass state, initialize_state handles it
    try:
        app.invoke({"iterations":1})
        # Stream events for progress updates
        # for event in app.stream({}):
        #     for node, output in event.items():
        #         print(f"\n--- Completed Node: {node} ---")
        #         # Optionally print state details or outputs here for debugging
        #         # print(f"Output: {str(output)[:500]}...")
        #     print("\n") # Add spacing between node completions
    except Exception as e:
        print(f"\n--- Workflow Error ---")
        print(f"An error occurred during graph execution: {repr(e)}")
        # You might want to inspect the final state here if possible
    finally:
        print("--- Agent Workflow Finished ---")

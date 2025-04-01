import pandas as pd
import numpy as np
from tabulate import tabulate
import json
import warnings
import time

warnings.simplefilter(action='ignore', category=UserWarning)

# Load Data
df = pd.read_csv('data_processed.csv')

# Section 1: Preview of Data
print("\n" + "="*50 + "\n First Few Rows of Data\n" + "="*50)
print(df.head().to_string())

# Section 2: Column Names and Data Types
print("\n" + "="*50 + "\n Column Names and Data Types\n" + "="*50)
print(df.dtypes)

# Section 3: Missing Values Per Column
print("\n" + "="*50 + "\n Missing Values Per Column\n" + "="*50)
print(df.isnull().sum())

# Section 4: Statistical Summary
print("\n" + "="*50 + "\n Statistical Summary\n" + "="*50)
print(df.describe(include='all').to_string())

# Section 5: Duplicate Rows
print("\n" + "="*50 + "\n Duplicate Rows Count\n" + "="*50)
print(f"Total Duplicate Rows: {df.duplicated().sum()}")

# Section 6: Outliers Using IQR
Q1 = df.select_dtypes(include=['number']).quantile(0.25)
Q3 = df.select_dtypes(include=['number']).quantile(0.75)
IQR = Q3 - Q1
outliers = ((df.select_dtypes(include=['number']) < (Q1 - 1.5 * IQR)) | 
            (df.select_dtypes(include=['number']) > (Q3 + 1.5 * IQR))).sum()

print("\n" + "="*50 + "\n Outliers Count Per Column\n" + "="*50)
print(outliers)

# Section 7: Unique Values for Categorical Columns (Fixing TypeError)
print("\n" + "="*50 + "\n Unique Values in Categorical Columns\n" + "="*50)
for col in df.select_dtypes(include=['object']).columns:
    try:
        unique_values = df[col].dropna().apply(lambda x: str(x) if isinstance(x, dict) else x).unique().tolist()
        if len(unique_values) < 10:  # Print only if count is less than 10
            print(f"\n{col}:", json.dumps(unique_values, indent=2))
        else:
            print(f"\n{col}: [About {len(unique_values) } unique values, to large to be displayed]")
    except Exception as e:
        print(f" Skipping {col} due to error: {e}")


# Section 9: Correlation Matrix

df_numeric = df.select_dtypes(include=[np.number])  
cov_matrix = df_numeric.cov()  
std_dev = np.sqrt(np.diag(cov_matrix))
corr_matrix = cov_matrix / np.outer(std_dev, std_dev)
corr_matrix = np.nan_to_num(corr_matrix)  # Handle NaNs

corr_df = pd.DataFrame(corr_matrix, index=df_numeric.columns, columns=df_numeric.columns)

print("\n" + "="*50 + "\n Correlation Matrix\n" + "="*50)
print(tabulate(corr_df.round(4), headers='keys', tablefmt='grid'))

# Section 10: Detecting Potential Datetime Columns
print("\n" + "="*50 + "\n Potential Datetime Columns\n" + "="*50)
for col in df.select_dtypes(include=['object']).columns:
    try:
        df[col] = pd.to_datetime(df[col], errors='coerce')  # Convert to datetime where possible
        if df[col].notna().all():
            print(f" {col}: Potential datetime column")
    except Exception as e:
        print(f" Skipping {col} due to error: {e}")

# Section 11: Detecting Low Variance Columns
low_variance = df.select_dtypes(include=['number']).var() < 0.1
print("\n" + "="*50 + "\n Low Variance Columns\n" + "="*50)
print(low_variance[low_variance].index.tolist())

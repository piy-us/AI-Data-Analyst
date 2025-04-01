Execution successful. Output:
**Starting Data Cleaning Script**
Input file: D:/AI Data Analysis/output/data_processed.csv
Output file: D:/AI Data Analysis/output/data_processed.csv
Ensured base output directory exists: D:/AI Data Analysis/output
Ensured viz plot directory exists: D:/AI Data Analysis/output/saved_plots
Ensured trend plot directory exists: D:/AI Data Analysis/output/trend_plots
Successfully loaded D:/AI Data Analysis/output/data_processed.csv. Initial Shape: (100000, 11)
Initial dtypes:
Order ID                   object
Customer ID                object
Platform                   object
Order Date & Time          object
Delivery Time (Minutes)     int64
Product Category           object
Order Value (INR)           int64
Customer Feedback          object
Service Rating              int64
Delivery Delay              int64
Refund Requested            int64
dtype: object

--- Applying Step 5 (Part 1): Improve Consistency & Formatting ---
Object columns identified for potential trimming/case standardization: ['Order ID', 'Customer ID', 'Platform', 'Order Date & Time', 'Product Category', 'Customer Feedback']
Trimmed whitespace for column: 'Order ID'
Trimmed whitespace for column: 'Customer ID'
Trimmed whitespace for column: 'Platform'
Trimmed whitespace for column: 'Order Date & Time'
Trimmed whitespace for column: 'Product Category'
Trimmed whitespace for column: 'Customer Feedback'
Applied title case to column: 'Platform'
Applied title case to column: 'Product Category'
Applied lower case to column: 'Customer Feedback'
Skipping boolean check for non-string column: 'Delivery Delay'
Skipping boolean check for non-string column: 'Refund Requested'

--- Applying Step 1: Datatype Conversion ---
Converted 'Delivery Delay' to Integer (1 for Yes, 0 for No, <NA> for others).
Converted 'Refund Requested' to Integer (1 for Yes, 0 for No, <NA> for others).
Skipping 'Order Date & Time' conversion as per plan (focus on consistency).

--- Applying Step 2: Handle Missing Values ---
Checking for missing values after initial steps:
Delivery Delay      100000
Refund Requested    100000
dtype: int64
Warning: 200000 missing values detected after initial steps. No imputation applied per plan.

--- Applying Step 3: Handle Duplicate Rows ---
No duplicate rows found, no action required as per plan.

--- Applying Step 4: Handle Outliers ---
No outlier treatment applied to 'Delivery Time (Minutes)' or 'Order Value (INR)' as per plan.

--- Applying Step 5 (Part 2): Improve Consistency & Formatting (`Order Date & Time`) ---
'Order Date & Time' format appears consistent with MM:SS.f pattern (basic check).
Keeping 'Order Date & Time' as object type after basic consistency checks as per plan.

--- Applying Step 6: Minimal Feature Engineering ---
No feature engineering (e.g., extracting time components) applied in this script as per plan.

--- Final Data Check ---
Final data shape: (100000, 11)
Final dtypes:
Order ID                   object
Customer ID                object
Platform                   object
Order Date & Time          object
Delivery Time (Minutes)     int64
Product Category           object
Order Value (INR)           int64
Customer Feedback          object
Service Rating              int64
Delivery Delay              Int64
Refund Requested            Int64
dtype: object
Final missing values count:
Order ID                        0
Customer ID                     0
Platform                        0
Order Date & Time               0
Delivery Time (Minutes)         0
Product Category                0
Order Value (INR)               0
Customer Feedback               0
Service Rating                  0
Delivery Delay             100000
Refund Requested           100000
dtype: int64
Sample of cleaned data (first 5 rows):
+----+------------+---------------+------------+---------------------+---------------------------+---------------------+---------------------+-------------------------------+------------------+------------------+--------------------+
|    | Order ID   | Customer ID   | Platform   | Order Date & Time   |   Delivery Time (Minutes) | Product Category    |   Order Value (INR) | Customer Feedback             |   Service Rating | Delivery Delay   | Refund Requested   |
|----+------------+---------------+------------+---------------------+---------------------------+---------------------+---------------------+-------------------------------+------------------+------------------+--------------------|
|  0 | ORD000001  | CUST2824      | Jiomart    | 19:29.5             |                        30 | Fruits & Vegetables |                 382 | fast delivery, great service! |                5 | <NA>             | <NA>               |
|  1 | ORD000002  | CUST1409      | Blinkit    | 54:29.5             |                        16 | Dairy               |                 279 | quick and reliable!           |                5 | <NA>             | <NA>               |
|  2 | ORD000003  | CUST5506      | Jiomart    | 21:29.5             |                        25 | Beverages           |                 599 | items missing from order.     |                2 | <NA>             | <NA>               |
|  3 | ORD000004  | CUST5012      | Jiomart    | 19:29.5             |                        42 | Beverages           |                 946 | items missing from order.     |                2 | <NA>             | <NA>               |
|  4 | ORD000005  | CUST4657      | Blinkit    | 49:29.5             |                        30 | Beverages           |                 334 | fast delivery, great service! |                5 | <NA>             | <NA>               |
+----+------------+---------------+------------+---------------------+---------------------------+---------------------+---------------------+-------------------------------+------------------+------------------+--------------------+

** Cleaned data saved successfully to D:/AI Data Analysis/output/data_processed.csv **

**Finished Data Cleaning Script**

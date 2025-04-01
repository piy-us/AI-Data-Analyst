Execution successful. Output:
Successfully loaded data from D:/AI Data Analysis/output\data_processed.csv

==================================================
 First Few Rows of Data
==================================================
    Order ID Customer ID Platform Order Date & Time  Delivery Time (Minutes)     Product Category  Order Value (INR)              Customer Feedback  Service Rating  Delivery Delay  Refund Requested
0  ORD000001    CUST2824  Jiomart           19:29.5                       30  Fruits & Vegetables                382  fast delivery, great service!               5             NaN               NaN
1  ORD000002    CUST1409  Blinkit           54:29.5                       16                Dairy                279            quick and reliable!               5             NaN               NaN
2  ORD000003    CUST5506  Jiomart           21:29.5                       25            Beverages                599      items missing from order.               2             NaN               NaN
3  ORD000004    CUST5012  Jiomart           19:29.5                       42            Beverages                946      items missing from order.               2             NaN               NaN
4  ORD000005    CUST4657  Blinkit           49:29.5                       30            Beverages                334  fast delivery, great service!               5             NaN               NaN

==================================================
 Column Names and Data Types
==================================================
Order ID                    object
Customer ID                 object
Platform                    object
Order Date & Time           object
Delivery Time (Minutes)      int64
Product Category            object
Order Value (INR)            int64
Customer Feedback           object
Service Rating               int64
Delivery Delay             float64
Refund Requested           float64
dtype: object

==================================================
 Missing Values Per Column
==================================================
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

==================================================
 Statistical Summary
==================================================
Numeric Columns Summary:
       Delivery Time (Minutes)  Order Value (INR)  Service Rating  Delivery Delay  Refund Requested
count            100000.000000      100000.000000   100000.000000             0.0               0.0
mean                 29.536140         590.994400        3.240790             NaN               NaN
std                   9.958933         417.409058        1.575962             NaN               NaN
min                   5.000000          50.000000        1.000000             NaN               NaN
25%                  23.000000         283.000000        2.000000             NaN               NaN
50%                  30.000000         481.000000        3.000000             NaN               NaN
75%                  36.000000         770.000000        5.000000             NaN               NaN
max                  76.000000        2000.000000        5.000000             NaN               NaN

Categorical/Object Columns Summary:
         Order ID Customer ID          Platform Order Date & Time Product Category         Customer Feedback
count      100000      100000            100000            100000           100000                    100000
unique     100000        9000                 3                60                6                        13
top     ORD000001    CUST8779  Swiggy Instamart           50:29.5            Dairy  easy to order, loved it!
freq            1          26             33449              1755            16857                      7791

==================================================
 Duplicate Rows Count
==================================================
Total Duplicate Rows: 0

==================================================
 Outliers Count Per Column (IQR Method)
==================================================
Delivery Time (Minutes)     475
Order Value (INR)          4360
Service Rating                0
Delivery Delay                0
Refund Requested              0
dtype: int64

==================================================
 Unique Values in Categorical Columns
==================================================

Order ID: [About 100000 unique values, showing first 20]
[
  "ORD000001",
  "ORD000002",
  "ORD000003",
  "ORD000004",
  "ORD000005",
  "ORD000006",
  "ORD000007",
  "ORD000008",
  "ORD000009",
  "ORD000010",
  "ORD000011",
  "ORD000012",
  "ORD000013",
  "ORD000014",
  "ORD000015",
  "ORD000016",
  "ORD000017",
  "ORD000018",
  "ORD000019",
  "ORD000020"
]

Customer ID: [About 9000 unique values, showing first 20]
[
  "CUST2824",
  "CUST1409",
  "CUST5506",
  "CUST5012",
  "CUST4657",
  "CUST3286",
  "CUST2679",
  "CUST9935",
  "CUST2424",
  "CUST7912",
  "CUST1520",
  "CUST1488",
  "CUST2535",
  "CUST4582",
  "CUST4811",
  "CUST9279",
  "CUST1434",
  "CUST4257",
  "CUST9928",
  "CUST7873"
]

Platform (Top 3 unique values):
[
  "Jiomart",
  "Blinkit",
  "Swiggy Instamart"
]

Order Date & Time: [About 60 unique values, showing first 20]
[
  "19:29.5",
  "54:29.5",
  "21:29.5",
  "49:29.5",
  "36:29.5",
  "22:29.5",
  "50:29.5",
  "51:29.5",
  "08:29.5",
  "32:29.5",
  "12:29.5",
  "27:29.5",
  "07:29.5",
  "58:29.5",
  "23:29.5",
  "15:29.5",
  "20:29.5",
  "44:29.5",
  "57:29.5",
  "01:29.5"
]

Product Category (Top 6 unique values):
[
  "Fruits & Vegetables",
  "Dairy",
  "Beverages",
  "Personal Care",
  "Grocery",
  "Snacks"
]

Customer Feedback (Top 13 unique values):
[
  "fast delivery, great service!",
  "quick and reliable!",
  "items missing from order.",
  "horrible experience, never ordering again.",
  "very satisfied with the service.",
  "very late delivery, not happy.",
  "excellent experience!",
  "easy to order, loved it!",
  "good quality products.",
  "not fresh, disappointed.",
  "wrong item delivered.",
  "delivery person was rude.",
  "packaging could be better."
]

==================================================
 Correlation Matrix
==================================================
+-------------------------+---------------------------+---------------------+------------------+------------------+--------------------+
|                         |   Delivery Time (Minutes) |   Order Value (INR) |   Service Rating |   Delivery Delay |   Refund Requested |
+=========================+===========================+=====================+==================+==================+====================+
| Delivery Time (Minutes) |                    1      |              0.0072 |           0.0001 |              nan |                nan |
+-------------------------+---------------------------+---------------------+------------------+------------------+--------------------+
| Order Value (INR)       |                    0.0072 |              1      |          -0.0027 |              nan |                nan |
+-------------------------+---------------------------+---------------------+------------------+------------------+--------------------+
| Service Rating          |                    0.0001 |             -0.0027 |           1      |              nan |                nan |
+-------------------------+---------------------------+---------------------+------------------+------------------+--------------------+
| Delivery Delay          |                  nan      |            nan      |         nan      |              nan |                nan |
+-------------------------+---------------------------+---------------------+------------------+------------------+--------------------+
| Refund Requested        |                  nan      |            nan      |         nan      |              nan |                nan |
+-------------------------+---------------------------+---------------------+------------------+------------------+--------------------+

==================================================
 Potential Datetime Columns
==================================================
 No potential datetime columns detected among object columns.

==================================================
 Low Variance Numeric Columns (Variance < 0.1)
==================================================
No numeric columns found with variance < 0.1.

==================================================
 Summary Generation Complete 
==================================================

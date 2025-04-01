Execution successful. Output:

==================================================
 First Few Rows of Data
==================================================
    Order ID Customer ID Platform Order Date & Time  Delivery Time (Minutes)     Product Category  Order Value (INR)              Customer Feedback  Service Rating Delivery Delay Refund Requested
0  ORD000001    CUST2824  JioMart           19:29.5                       30  Fruits & Vegetables                382  Fast delivery, great service!               5             No               No
1  ORD000002    CUST1409  Blinkit           54:29.5                       16                Dairy                279            Quick and reliable!               5             No               No
2  ORD000003    CUST5506  JioMart           21:29.5                       25            Beverages                599      Items missing from order.               2             No              Yes
3  ORD000004    CUST5012  JioMart           19:29.5                       42            Beverages                946      Items missing from order.               2            Yes              Yes
4  ORD000005    CUST4657  Blinkit           49:29.5                       30            Beverages                334  Fast delivery, great service!               5             No               No

==================================================
 Column Names and Data Types
==================================================
Order ID                   object
Customer ID                object
Platform                   object
Order Date & Time          object
Delivery Time (Minutes)     int64
Product Category           object
Order Value (INR)           int64
Customer Feedback          object
Service Rating              int64
Delivery Delay             object
Refund Requested           object
dtype: object

==================================================
 Missing Values Per Column
==================================================
Order ID                   0
Customer ID                0
Platform                   0
Order Date & Time          0
Delivery Time (Minutes)    0
Product Category           0
Order Value (INR)          0
Customer Feedback          0
Service Rating             0
Delivery Delay             0
Refund Requested           0
dtype: int64

==================================================
 Statistical Summary
==================================================
         Order ID Customer ID          Platform Order Date & Time  Delivery Time (Minutes) Product Category  Order Value (INR)         Customer Feedback  Service Rating Delivery Delay Refund Requested
count      100000      100000            100000            100000            100000.000000           100000      100000.000000                    100000   100000.000000         100000           100000
unique     100000        9000                 3                60                      NaN                6                NaN                        13             NaN              2                2
top     ORD000001    CUST8779  Swiggy Instamart           50:29.5                      NaN            Dairy                NaN  Easy to order, loved it!             NaN             No               No
freq            1          26             33449              1755                      NaN            16857                NaN                      7791             NaN          86328            54181
mean          NaN         NaN               NaN               NaN                29.536140              NaN         590.994400                       NaN        3.240790            NaN              NaN
std           NaN         NaN               NaN               NaN                 9.958933              NaN         417.409058                       NaN        1.575962            NaN              NaN
min           NaN         NaN               NaN               NaN                 5.000000              NaN          50.000000                       NaN        1.000000            NaN              NaN
25%           NaN         NaN               NaN               NaN                23.000000              NaN         283.000000                       NaN        2.000000            NaN              NaN
50%           NaN         NaN               NaN               NaN                30.000000              NaN         481.000000                       NaN        3.000000            NaN              NaN
75%           NaN         NaN               NaN               NaN                36.000000              NaN         770.000000                       NaN        5.000000            NaN              NaN
max           NaN         NaN               NaN               NaN                76.000000              NaN        2000.000000                       NaN        5.000000            NaN              NaN

==================================================
 Duplicate Rows Count
==================================================
Total Duplicate Rows: 0

==================================================
 Outliers Count Per Column
==================================================
Delivery Time (Minutes)     475
Order Value (INR)          4360
Service Rating                0
dtype: int64

==================================================
 Unique Values in Categorical Columns
==================================================

Order ID: [About 100000 unique values, too large to be displayed]

Customer ID: [About 9000 unique values, too large to be displayed]

Platform: [
  "JioMart",
  "Blinkit",
  "Swiggy Instamart"
]

Order Date & Time: [About 60 unique values, too large to be displayed]

Product Category: [
  "Fruits & Vegetables",
  "Dairy",
  "Beverages",
  "Personal Care",
  "Grocery",
  "Snacks"
]

Customer Feedback: [About 13 unique values, too large to be displayed]

Delivery Delay: [
  "No",
  "Yes"
]

Refund Requested: [
  "No",
  "Yes"
]

==================================================
 Correlation Matrix
==================================================
+-------------------------+---------------------------+---------------------+------------------+
|                         |   Delivery Time (Minutes) |   Order Value (INR) |   Service Rating |
+=========================+===========================+=====================+==================+
| Delivery Time (Minutes) |                    1      |              0.0072 |           0.0001 |
+-------------------------+---------------------------+---------------------+------------------+
| Order Value (INR)       |                    0.0072 |              1      |          -0.0027 |
+-------------------------+---------------------------+---------------------+------------------+
| Service Rating          |                    0.0001 |             -0.0027 |           1      |
+-------------------------+---------------------------+---------------------+------------------+

==================================================
 Potential Datetime Columns
==================================================
 No potential datetime columns detected among object columns.

==================================================
 Low Variance Columns (Variance < 0.1)
==================================================
No numerical columns found with variance < 0.1.

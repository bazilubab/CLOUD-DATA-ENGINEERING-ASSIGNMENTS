import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==================================================
# STEP 1: DATA LOAD KARNA (CSV file ko read karna aur basic info dekhna)
# ==================================================

INPUT_FILE = "supermarket_sales_case_study.csv"
OUTPUT_FILE = "supermarket_sales_cleaned.csv"
TARGET = 100000

df = pd.read_csv(INPUT_FILE)

print("\nSTEP 1: DATA LOADED")
print("Initial rows and columns:", df.shape)
print("\nFirst 5 rows:")
print(df.head())
print("\nColumn names:")
print(df.columns.tolist())
print("\nData information:")
df.info()


# ==================================================
# STEP 2: INITIAL DATA AUDIT (Missing values aur duplicates check karna)
# ==================================================

audit_log = []

def record_audit(step_name, before, after):
    audit_log.append({
        "Step": step_name,
        "Rows Before": before,
        "Rows After": after,
        "Rows Removed": before - after
    })

print("\nSTEP 2: MISSING VALUES")
print(df.isnull().sum())

print("\nExact duplicate rows:", df.duplicated().sum())

print("\nDuplicate Invoice IDs:",
      df["Invoice ID"].duplicated().sum())

print("\nGender values:")
print(df["Gender"].unique())

print("\nPayment values:")
print(df["Payment"].unique())


# ==================================================
# STEP 3: EXACT DUPLICATES HATANA (Poori duplicate rows remove karna)
# ==================================================

before = len(df)

df = df.drop_duplicates().copy()

record_audit("Remove exact duplicates", before, len(df))

print("\nSTEP 3: EXACT DUPLICATES REMOVED")
print("Remaining exact duplicates:", df.duplicated().sum())


# ==================================================
# STEP 4: DUPLICATE INVOICE IDs RESOLVE KARNA (Last row ko rakhna kyunki woh correction hai)
# ==================================================

before = len(df)

df = df.drop_duplicates(
    subset=["Invoice ID"],
    keep="last"
).copy()

record_audit("Resolve duplicate Invoice IDs", before, len(df))

print("\nSTEP 4: DUPLICATE INVOICE IDs RESOLVED")
print("Remaining duplicate Invoice IDs:",
      df["Invoice ID"].duplicated().sum())


# ==================================================
# STEP 5: TEXT STANDARDIZE KARNA (Extra spaces hatana aur spellings theek karna)
# ==================================================

before = len(df)

for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].map(
        lambda x: x.strip().lower() if isinstance(x, str) else x
    )

# Gender ki spellings standardise karna
df["Gender"] = df["Gender"].replace({
    "m": "male",
    "f": "female"
})

df["Gender"] = df["Gender"].replace({
    "male": "Male",
    "female": "Female"
})

# Payment ki spellings standardise karna
df["Payment"] = df["Payment"].replace({
    "cash": "Cash",
    "credit card": "Credit card",
    "creditcard": "Credit card",
    "ewallet": "Ewallet",
    "e-wallet": "Ewallet",
    "e wallet": "Ewallet"
})

record_audit("Standardize text columns", before, len(df))

print("\nSTEP 5: STANDARDIZED VALUES")
print("Gender:", df["Gender"].unique())
print("Payment:", df["Payment"].unique())


# ==================================================
# STEP 6: NEGATIVE QUANTITIES FIX KARNA (Minus sign ko abs() se positive banana)
# ==================================================

before = len(df)

df["Quantity"] = pd.to_numeric(
    df["Quantity"], errors="coerce"
)

df["Quantity"] = df["Quantity"].abs()

record_audit("Fix negative Quantity", before, len(df))

print("\nSTEP 6: NEGATIVE QUANTITY FIXED")
print("Negative quantities remaining:",
      (df["Quantity"] < 0).sum())


# ==================================================
# STEP 7: TOTAL CHECK KARNA (Total column ko numeric me convert karna)
# ==================================================

df["Total"] = pd.to_numeric(
    df["Total"], errors="coerce"
)

print("\nSTEP 7: TOTAL CHECK")
print("Missing Total values:", df["Total"].isnull().sum())
print(df["Total"].describe())

# Do not recalculate Total without confirming
# the formula specified by the assignment.


# ==================================================
# STEP 8: REQUIRED COLUMNS CHECK KARNA
# ==================================================

required_columns = [
    "Invoice ID", "Branch", "Customer type", "Gender",
    "Quantity", "Total", "Date", "Time",
    "Payment", "Rating"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"These required columns are missing: {missing_columns}"
    )

print("\nSTEP 8: REQUIRED COLUMNS CHECKED")


# ==================================================
# STEP 9: MISSING VALUES HANDLE KARNA (Customer type me Unknown aur Rating me median dalna)
# ==================================================

# Missing Customer type me Unknown bharna
df["Customer type"] = df["Customer type"].fillna("Unknown")

# Rating ko numeric karke median se fill karna
df["Rating"] = pd.to_numeric(
    df["Rating"], errors="coerce"
)

median_rating = df["Rating"].median()

if pd.notna(median_rating):
    df["Rating"] = df["Rating"].fillna(median_rating)
else:
    print("Warning: Rating is completely missing; median unavailable.")

# Date ko datetime me convert karna aur missing dates wali rows drop karna
before = len(df)

df["Date"] = pd.to_datetime(
    df["Date"], errors="coerce"
)

df = df.dropna(subset=["Date"]).copy()

record_audit("Remove rows with missing/invalid Date",
             before, len(df))

print("\nSTEP 9: MISSING VALUES HANDLED")
print("Missing Customer type:",
      df["Customer type"].isnull().sum())
print("Missing Rating:", df["Rating"].isnull().sum())
print("Missing Date:", df["Date"].isnull().sum())


# ==================================================
# STEP 10: AUDIT TRAIL SAVE KARNA (Cleaning ka record CSV me save karna)
# ==================================================

audit_df = pd.DataFrame(audit_log)

print("\nSTEP 10: AUDIT TRAIL")
print(audit_df)

audit_df.to_csv("supermarket_audit_trail.csv", index=False)

print("Audit trail saved to supermarket_audit_trail.csv")


# ==================================================
# ANALYSIS 1: TIME COLUMNS BANANA (Date aur Time se Year, Quarter, Day, Hour nikalna)
# ==================================================

df["Time"] = pd.to_datetime(
    df["Time"].astype(str), errors="coerce"
)

df["Year"] = df["Date"].dt.year
df["Quarter Number"] = df["Date"].dt.quarter

df["Quarter"] = (
    df["Year"].astype(str)
    + "Q"
    + df["Quarter Number"].astype(str)
)

df["Day of Week"] = df["Date"].dt.day_name()
df["Hour"] = df["Time"].dt.hour

print("\nANALYSIS 1: TIME COLUMNS CREATED")
print(df[[
    "Date", "Time", "Year", "Quarter",
    "Day of Week", "Hour"
]].head())


# ==================================================
# ANALYSIS 2: TRADING DAY BUCKETS (Morning, Afternoon, Evening me transactions batna)
# ==================================================

def trading_period(hour):
    if pd.isna(hour):
        return "Unknown"
    elif 10 <= hour < 13:
        return "Morning"
    elif 13 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Outside trading hours"

df["Trading Period"] = df["Hour"].apply(trading_period)

period_hours = {
    "Morning": 3,
    "Afternoon": 4,
    "Evening": 4
}

period_summary = (
    df[df["Trading Period"].isin(period_hours)]
    .groupby("Trading Period")
    .size()
    .rename("Transactions")
    .reset_index()
)

period_summary["Hours"] = period_summary[
    "Trading Period"
].map(period_hours)

period_summary["Transactions per Hour"] = (
    period_summary["Transactions"] / period_summary["Hours"]
)

period_summary = period_summary.sort_values(
    "Transactions per Hour", ascending=False
)

print("\nANALYSIS 2: TRADING PERIOD SUMMARY")
print(period_summary)

period_summary.to_csv(
    "trading_period_summary.csv", index=False
)


# ==================================================
# ANALYSIS 3: BRANCH REVENUE VS TARGET ($100,000 target ke sath comparison)
# ==================================================

quarterly_revenue = (
    df.groupby(["Branch", "Year", "Quarter Number", "Quarter"],
               as_index=False)["Total"]
    .sum()
    .rename(columns={"Total": "Revenue"})
)

quarterly_revenue["Target"] = TARGET

quarterly_revenue["Variance"] = (
    quarterly_revenue["Revenue"] - quarterly_revenue["Target"]
)

quarterly_revenue["Percent of Target"] = (
    quarterly_revenue["Revenue"] / TARGET * 100
)

quarterly_revenue["Hit Target"] = (
    quarterly_revenue["Revenue"] >= TARGET
)

quarterly_revenue = quarterly_revenue.sort_values(
    ["Branch", "Year", "Quarter Number"]
)

print("\nANALYSIS 3: BRANCH QUARTERLY REVENUE")
print(quarterly_revenue)

quarterly_revenue.to_csv(
    "branch_quarterly_revenue.csv", index=False
)


# ==================================================
# ANALYSIS 4: BRANCH SUMMARY (Average revenue, best/worst quarter aur YoY growth nikalna)
# ==================================================

branch_summary = (
    quarterly_revenue.groupby("Branch")
    .agg(
        Average_Quarter_Revenue=("Revenue", "mean"),
        Quarters_Hit_Target=("Hit Target", "sum"),
        Total_Quarters=("Quarter", "count")
    )
    .reset_index()
)

best_quarter = quarterly_revenue.loc[
    quarterly_revenue.groupby("Branch")["Revenue"].idxmax(),
    ["Branch", "Quarter", "Revenue"]
].rename(columns={
    "Quarter": "Best Quarter",
    "Revenue": "Best Quarter Revenue"
})

worst_quarter = quarterly_revenue.loc[
    quarterly_revenue.groupby("Branch")["Revenue"].idxmin(),
    ["Branch", "Quarter", "Revenue"]
].rename(columns={
    "Quarter": "Worst Quarter",
    "Revenue": "Worst Quarter Revenue"
})

branch_summary = branch_summary.merge(
    best_quarter, on="Branch"
).merge(
    worst_quarter, on="Branch"
)

# Year-over-year revenue growth calculate karna
yearly_revenue = (
    df.groupby(["Branch", "Year"])["Total"]
    .sum()
    .unstack()
)

if 2023 in yearly_revenue.columns and 2024 in yearly_revenue.columns:
    yearly_revenue["YoY Growth %"] = (
        (yearly_revenue[2024] / yearly_revenue[2023]) - 1
    ) * 100

    branch_summary = branch_summary.merge(
        yearly_revenue[["YoY Growth %"]].reset_index(),
        on="Branch", how="left"
    )

print("\nANALYSIS 4: BRANCH SUMMARY")
print(branch_summary)

branch_summary.to_csv("branch_summary.csv", index=False)


# ==================================================
# ANALYSIS 5A: BUSY WEEKDAYS (Haftay ke dinon ke hisab se transactions nikalna)
# ==================================================

weekday_transactions = (
    df.groupby("Day of Week")
    .size()
    .rename("Transactions")
    .reset_index()
)

weekday_dates = (
    df[["Date", "Day of Week"]]
    .drop_duplicates()
    .groupby("Day of Week")
    .size()
    .rename("Number of Days")
    .reset_index()
)

weekday_summary = weekday_transactions.merge(
    weekday_dates, on="Day of Week"
)

weekday_summary["Average Transactions per Day"] = (
    weekday_summary["Transactions"]
    / weekday_summary["Number of Days"]
)

weekday_order = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

weekday_summary["Day of Week"] = pd.Categorical(
    weekday_summary["Day of Week"],
    categories=weekday_order, ordered=True
)

weekday_summary = weekday_summary.sort_values("Day of Week")

print("\nANALYSIS 5A: BUSY WEEKDAYS")
print(weekday_summary)

weekday_summary.to_csv("weekday_summary.csv", index=False)


# ==================================================
# ANALYSIS 5B: WEEKDAY AND HOUR HEATMAP (Din aur ghantay ka heatmap banana)
# ==================================================

valid_hours = df[df["Hour"].between(10, 20)].copy()

daily_hour_counts = (
    valid_hours.groupby(["Date", "Day of Week", "Hour"])
    .size()
    .rename("Transactions")
    .reset_index()
)

heatmap_data = daily_hour_counts.pivot_table(
    index="Day of Week",
    columns="Hour",
    values="Transactions",
    aggfunc="mean",
    observed=False
)

heatmap_data = heatmap_data.reindex(weekday_order)

print("\nANALYSIS 5B: WEEKDAY-HOUR HEATMAP DATA")
print(heatmap_data)

plt.figure(figsize=(12, 6))
plt.imshow(heatmap_data, aspect="auto", cmap="YlOrRd")
plt.colorbar(label="Average transactions")
plt.xticks(
    range(len(heatmap_data.columns)),
    heatmap_data.columns
)
plt.yticks(
    range(len(heatmap_data.index)),
    heatmap_data.index
)
plt.xlabel("Hour of Day")
plt.ylabel("Day of Week")
plt.title("Average Transactions by Weekday and Hour")
plt.tight_layout()
plt.savefig("weekday_hour_heatmap.png", dpi=150)
plt.show()


# ==================================================
# ANALYSIS 6A: BRANCH QUARTERLY REVENUE PLOT (Har branch ka line chart banana)
# ==================================================

for branch in sorted(quarterly_revenue["Branch"].dropna().unique()):
    branch_data = quarterly_revenue[
        quarterly_revenue["Branch"] == branch
    ].sort_values(["Year", "Quarter Number"])

    plt.figure(figsize=(10, 5))

    plt.plot(
        branch_data["Quarter"],
        branch_data["Revenue"],
        marker="o",
        label="Revenue"
    )

    plt.axhline(
        y=TARGET,
        linestyle="--",
        label="$100,000 Target"
    )

    plt.title(f"Quarterly Revenue - Branch {branch}")
    plt.xlabel("Quarter")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    safe_branch = str(branch).replace("/", "_").replace(" ", "_")

    plt.savefig(
        f"branch_{safe_branch}_quarterly_revenue.png",
        dpi=150
    )
    plt.show()


# ==================================================
# ANALYSIS 6B: EXPORT CLEAN DATA (Cleaned dataframe ko CSV me save karna)
# ==================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\nCLEANED DATA SAVED:", OUTPUT_FILE)


# ==================================================
# ANALYSIS 6C: MANAGEMENT SUMMARY (Management ke liye summary text file banana)
# ==================================================

total_revenue = df["Total"].sum()
total_transactions = len(df)

if not quarterly_revenue.empty:
    best_overall = quarterly_revenue.loc[
        quarterly_revenue["Revenue"].idxmax()
    ]

    worst_overall = quarterly_revenue.loc[
        quarterly_revenue["Revenue"].idxmin()
    ]

    quarters_hit = int(quarterly_revenue["Hit Target"].sum())

    summary_lines = [
        f"Total revenue across all branches: ${total_revenue:,.2f}.",
        f"Total transactions in the cleaned data: {total_transactions}.",
        f"Best branch-quarter: {best_overall['Branch']}, "
        f"{best_overall['Quarter']} "
        f"(${best_overall['Revenue']:,.2f}).",
        f"Weakest branch-quarter: {worst_overall['Branch']}, "
        f"{worst_overall['Quarter']} "
        f"(${worst_overall['Revenue']:,.2f}).",
        f"Branch-quarter results meeting the $100,000 target: "
        f"{quarters_hit} out of {len(quarterly_revenue)}."
    ]
else:
    summary_lines = [
        "No quarterly revenue data was available."
    ]

print("\nMANAGEMENT SUMMARY")

for line in summary_lines:
    print(line)

with open("management_summary.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(summary_lines))

print("\nALL STEPS FINISHED.")
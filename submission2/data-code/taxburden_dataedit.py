import pandas as pd
import numpy as np

# Load Data
cig_data = pd.read_csv("/Users/ellenwu/homework3_attempt1-/data/input/The_Tax_Burden_on_Tobacco__1970-2019_20250304.csv")
cpi_data = pd.read_excel("/Users/ellenwu/homework3_attempt1-/data/input/SeriesReport-20250304165118_4f02a8.xlsx", skiprows=11)

# 🛠️ Fix 1: Ensure 'Year' is an integer in both datasets
cig_data["Year"] = cig_data["Year"].astype(int)
cpi_data["Year"] = cpi_data["Year"].astype(int)

# Cleaning Tobacco Data
cig_data["measure"] = cig_data["SubMeasureDesc"].map({
    "Average Cost per pack": "cost_per_pack",
    "Cigarette Consumption (Pack Sales Per Capita)": "sales_per_capita",
    "Federal and State tax as a Percentage of Retail Price": "tax_percent",
    "Federal and State Tax per pack": "tax_dollar",
    "Gross Cigarette Tax Revenue": "tax_revenue",
    "State Tax per pack": "tax_state"
})

cig_data = cig_data.rename(columns={"LocationAbbr": "state_abb", "LocationDesc": "state", "Data_Value": "value"})
cig_data = cig_data[["state_abb", "state", "Year", "value", "measure"]]

# Pivot Data
final_data = cig_data.pivot(index=["state", "Year"], columns="measure", values="value").reset_index()

# 🛠️ Fix 2: Drop incorrect year values before merging
final_data = final_data[(final_data["Year"] >= 1970) & (final_data["Year"] <= 2019)]

# Cleaning CPI Data
print("Columns in DataFrame after skipping rows:", cpi_data.columns.tolist()) 

# 🛠️ Fix 3: Drop 'HALF1' and 'HALF2' columns from CPI dataset
cpi_data = cpi_data.drop(columns=["HALF1", "HALF2"], errors="ignore")

cpi_data = cpi_data.melt(id_vars=["Year"], 
                          value_vars=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                          var_name="month", 
                          value_name="index")

cpi_data = cpi_data.groupby("Year", as_index=False).agg({"index": "mean"})

# Merge CPI Data
final_data = final_data.merge(cpi_data, on="Year", how="left")  # 🛠️ Fix 4: Use 'left' instead of 'outer'

# 🛠️ Fix 5: Fill Missing CPI Values
final_data["index"].fillna(final_data["index"].mean(), inplace=True)

# Adjust to 2010 Dollars
final_data["price_cpi"] = final_data["cost_per_pack"] * (218 / final_data["index"])

# Check Fixed Year Range
print(final_data[["Year"]].drop_duplicates().sort_values("Year"))

# Save Data
final_data.to_csv("/Users/ellenwu/homework3/data/output/ftaxburden_data.csv", index=False)

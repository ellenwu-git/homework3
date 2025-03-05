# Meta --------------------------------------------------------------------

## Title:         CDC Tax Burden on Tobacco
## Author:        Ellen Wu
## Date Created:  3/4/2025
## Date Edited:   
## Description:   Clean and analyze CDC data 

import pandas as pd 
import numpy as np

# Read data ---------------------------------------------------------------
cig_data = pd.read_csv("/Users/ellenwu/homework3_attempt1-/data/input/The_Tax_Burden_on_Tobacco__1970-2019_20250304.csv")
cpi_data = pd.read_excel("/Users/ellenwu/homework3_attempt1-/data/input/SeriesReport-20250304165118_4f02a8.xlsx", skiprows=11)

# Clean tobacco data ------------------------------------------------------
def map_measure(desc):
    mapping = {
        "Average Cost per pack": "cost_per_pack",
        "Cigarette Consumption (Pack Sales Per Capita)": "sales_per_capita",
        "Federal and State tax as a Percentage of Retail Price": "tax_percent",
        "Federal and State Tax per pack": "tax_dollar",
        "Gross Cigarette Tax Revenue": "tax_revenue",
        "State Tax per pack": "tax_state"
    }
    return mapping.get(desc, None)

cig_data['measure'] = cig_data['SubMeasureDesc'].map(map_measure)

cig_data = cig_data[['LocationAbbr', 'LocationDesc', 'Year', 'Data_Value', 'measure']].rename(
    columns={
        'LocationAbbr': 'state_abb',
        'LocationDesc': 'state',
        'Data_Value': 'value'
    }
)

final_data = cig_data.pivot_table(index=['state', 'Year'], 
                                  columns='measure', 
                                  values='value').reset_index()

final_data = final_data.sort_values(by=['state', 'Year'])

# Clean CPI data ----------------------------------------------------------
cpi_data = cpi_data.melt(id_vars=['Year'], 
                         value_vars=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                         var_name='month', 
                         value_name='index')

cpi_data = cpi_data.groupby('Year', as_index=False).agg({'index': 'mean'})

# Form final dataset ------------------------------------------------------
# adjust to 2010 dollars (using 2010 CPI = 218)
final_data = final_data.merge(cpi_data, on='Year', how='left')

final_data['price_cpi'] = final_data['cost_per_pack'] * (218 / final_data['index'])

# Write output files ------------------------------------------------------
final_data.to_csv("/Users/ellenwu/homework3_attempt1-/data/output/TaxBurden_Data.txt", sep='\t', index=False)
final_data.to_csv("/Users/ellenwu/homework3_attempt1-/data/output/TaxBurden_Data.csv", index=False)
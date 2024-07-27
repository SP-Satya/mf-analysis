# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 18:43:36 2024

@author: Satya Prakash
"""

import os
import pandas as pd
os.chdir("data")
file_list=os.listdir()

FILE_NAME="Portfolios.xlsx"

# =============================================================================
# Read the mutual fund perfomance from the files
# Merge the stats in a single dataframe
# =============================================================================
file_count=0
for filename in file_list:
    #print(filename)
    if filename == FILE_NAME:
        continue
    elif file_count == 0:
        data=pd.read_excel(filename, sheet_name='Sheet1',na_values=['-'], skiprows=[0])
        file_count = file_count+1
    else:
        new_data=pd.read_excel(filename, sheet_name='Sheet1',na_values=['-'], skiprows=[0])
        #print(new_data.columns)
        frames = [data, new_data]
        data = pd.concat(frames)

data.columns

data['1Y']=round(data['1Y']*100,2)
data['2Y']=round(data['2Y']*100,2)
data['3Y']=round(data['3Y']*100,2)
data['5Y']=round(data['5Y']*100,2)
data['10Y']=round(data['10Y']*100,2)

# =============================================================================
# 
# collect the 75% percentile of the mutual fund perfomances over the years
# =============================================================================
stats_df=data.describe()
Y1_75=stats_df['1Y']['75%']
Y2_75=stats_df['2Y']['75%']
Y3_75=stats_df['3Y']['75%']
Y5_75=stats_df['5Y']['75%']
Y10_75=stats_df['10Y']['75%']
Y10_50=stats_df['10Y']['50%']
        
        

mask = (data['1Y'] > Y1_75) & (data['2Y'] >Y2_75) & (data['3Y'] >Y3_75) & (data['5Y'] > Y5_75) & (data['10Y'] >Y10_75)  
mask
data_all_75_df = data.loc[mask]

print("1Y 75 percentile:",Y1_75)
print("2Y 75 percentile:",Y2_75)
print("3Y 75 percentile:",Y3_75)
print("5Y 75 percentile:",Y5_75)
print("10Y 75 percentile:",Y10_75)
print("10Y 50 percentile:",Y10_50)


# =============================================================================
# Extract the mutual funds which are consistently in top 25% in terms of giving return 
# =============================================================================
print("********************* Top 1 count = ", len(data_all_75_df))
mask = (data['1Y'] > Y1_75) & (data['2Y'] >Y2_75) & (data['3Y'] >Y3_75) & (data['5Y'] > Y5_75) & (data['10Y'] >Y10_50) 
data_a_75_50_df = data.loc[mask]

# =============================================================================
# Extract the mutual funds which are consistently in top 25% in terms of giving return 
# Exception being for the old time where it is among top 50%
# =============================================================================  
print("********************* Top 2 count = ",  len(data_a_75_50_df))
data_a_75_50_df.to_html()

# =============================================================================
# 
# Read your own investment data
# =============================================================================
os.chdir("../investments")
##################################################################
investment_filename='CANHoldingReport.xls'
investment=pd.read_excel(investment_filename, sheet_name='CANHoldingReport',na_values=['-'], skiprows=[0])

data_all_75_df=data_all_75_df.assign( Invested ='No')
data_all_75_df=data_all_75_df.assign( Units = '-' )
data_all_75_df=data_all_75_df.assign( NAV ='-')
data_all_75_df=data_all_75_df.assign( Current_Value ='-')

# =============================================================================
# Mapping if different system using slighly different name for the same mutual fund
# =============================================================================
myPortfolio = {
    "HDFC Top 100 Fund - Direct Plan - Growth Option" : "HDFC Top 100 Fund - Direct Plan - Growth",
    "HSBC Midcap Fund - Direct Growth" : "HSBC Mid Cap Fund - Direct Plan - Growth",
    "ICICI Prudential Banking and Financial Services Fund - Direct Plan - Growth" : "ICICI Prudential Banking and Financial Services Fund - Direct Plan - Growth",
    "ICICI Prudential Bluechip Fund - Direct Plan - Growth" : "ICICI Prudential Bluechip Fund - Direct Plan - Growth",
    "ICICI Prudential Infrastructure Fund - Direct Plan - Growth" : "ICICI Prudential Infrastructure Fund - Direct Plan - Growth",
    "ICICI Prudential Technology Fund - Direct Plan - Growth": "ICICI Prudential Technology Fund - Direct Plan - Growth",
    "quant Infrastructure Fund (a Sectorial/Thematic Fund)-Direct Growth Plan-Growth" : "Quant Infrastructure Fund - Direct Plan - Growth",
    "quant Large & Mid Cap Fund (a Large & Midcap Fund)-Direct Growth Plan-Growth" : "Quant Large and Mid Cap Fund - Direct Plan - Growth",
    "quant Mid Cap Fund (a Mid Cap Fund)-Direct Growth Plan-Growth" : "Quant Mid Cap Fund - Direct Plan - Growth",
    "quant Small Cap Fund (a Small Cap Fund)-Direct Growth Plan-Growth" : "Quant Small Cap Fund - Direct Plan - Growth",
    "SBI PSU Fund - Direct Plan - Growth" : "SBI PSU Fund - Direct Plan - Growth",
    "SBI Small Cap Fund-Direct-Growth": "SBI Small Cap Fund - Direct Plan - Growth"
}
       
 
# =============================================================================
# Now get the Top performing mutual fund result merged with your investment in these funds
# =============================================================================
for index, row in investment.iterrows():
    invested_fund_name=row['Scheme Details']
    units = row['Units']
    nav = row ['Current Value based on NAV']
    current_value = row['Current Value']
    
    #print (invested_fund_name)
    
    if invested_fund_name in myPortfolio.keys():
        fund_name=myPortfolio.get(invested_fund_name)
    else:
        fund_name= invested_fund_name
        
    
    top1_fund_detail=data_all_75_df[data_all_75_df['Scheme Name'] == fund_name]
    
    
    if len(top1_fund_detail) == 1:
        #print("Add investment value in existing Top1 record")
        top1_nav = top1_fund_detail['NAV'].item()
        if top1_nav == nav:
            units = units + top1_fund_detail['Units']
            current_value = current_value + top1_fund_detail['Current_Value']
        else:
            data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'Invested'] = 'Yes, In Top1'
            data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'NAV'] = nav
            
        data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'Units'] = units
        data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'Current_Value'] = current_value
    elif len(top1_fund_detail) == 0:
        #print("Investment not in top1 list")
        # get detail from entire fund set
        all_data_fund_detail = data[data['Scheme Name'] == fund_name]
        
        if len(all_data_fund_detail) == 1:
            #print("Insert the investment, this is not in Top1 list")
            frames = [data_all_75_df, all_data_fund_detail]
            data_all_75_df = pd.concat(frames)
            
            data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'Invested'] = 'Yes, Not in Top1'
            data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'Units'] = units
            data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'NAV'] = nav
            data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'Current_Value'] = current_value
            
        elif len(all_data_fund_detail) == 0:
            print (invested_fund_name)
            print("Not found, map in the dictionary")
            #data_all_75_df.insert(len(data_all_75_df), 'Scheme Name', fund_name)
            #data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'Units'] = units
            #data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'NAV'] = nav
            #data_all_75_df.loc[data_all_75_df['Scheme Name'] == fund_name, 'Current_Value'] = current_value
            new_r  = {'Scheme Name': fund_name, 'Invested': 'Yes, Not in Top1', 'Units': units, 'NAV' : nav, 'Current_Value' : current_value }
            data_all_75_df.loc[len(data_all_75_df)] = new_r
        else:
            print (invested_fund_name)
            print("should not happen,.. ERROR")
    else:
        print (invested_fund_name)
        print("should not appear more than once in Top1 list,.. ERROR")
  
        
    data.columns   
    
# =============================================================================
# write the results to a excet file
# =============================================================================
os.chdir("..")
with pd.ExcelWriter(FILE_NAME) as writer:  
    data_all_75_df.to_excel(writer, sheet_name='Top1')
    data_a_75_50_df.to_excel(writer, sheet_name='Top2')
    data.to_excel(writer, sheet_name='Portfolios')


#               


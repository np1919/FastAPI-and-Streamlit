import datetime as dt
import pandas as pd
import numpy as np
from database import engine, get_db
from my_url import _SQLALCHEMY_DATABASE_URL
from dunnhumby_data_warehouse import DunnHumbyDataWarehouse
import pandas as pd 
a = DunnHumbyDataWarehouse()


transactions = a.get_table('transaction_data')
transactions = transactions.drop('index',axis=1)

## ADDING DATETIME
# add datetime values. this should be back-integrated with the data ingestion procedure, now that we have it
day1 = dt.datetime(2004, 3, 23) # as derived in transactions notebook; datetime for 'DAY' == 1
ineedthismany = transactions['DAY'].max()
last = day1 + dt.timedelta(days=int(ineedthismany))
date_range = pd.date_range(day1, last) # date range for our data
# map datetime index to DAY; enumerate() indexes from 0, so we add 1
date_map = {i+1:x for i, x in enumerate(date_range)}
# truncate data
output = transactions['TRANS_TIME'].astype(str).str.zfill(4)
# split to hours and minutes
hours = output.str[:2]
minutes = output.str[2:]
# convert to timedelta
hours = pd.to_timedelta(hours.astype('int'), unit='hour')
minutes = pd.to_timedelta(minutes.astype('int'), unit='minute')
time_of_transaction = hours + minutes
# add date and time
transactions['datetime'] = transactions['DAY'].map(date_map) + time_of_transaction



### DATA CLEANING

# filtering empty sales rows..
transactions = transactions.loc[(transactions['QUANTITY'] > 0) & 
                (transactions['SALES_VALUE'] > 0)]
# filtering on datetime (data acquisition inconsistency?)
transactions = transactions[(transactions['datetime'] >= "2004-7-1") &
                (transactions['datetime'] < "2006-3-1")]


###  PRODUCT 
prod = a.get_table('product')
#pd.read_csv('../data/product.csv')
prod.drop('index', axis=1, inplace=True)
merged = transactions.merge(prod.drop('CURR_SIZE_OF_PRODUCT', axis=1), on='PRODUCT_ID')


### CLEANING BASED ON PRODUCT INFO
# Remove Gasoline Sales
merged.drop(merged[merged['SUB_COMMODITY_DESC']=='GASOLINE-REG UNLEADED'].index, axis=0, inplace=True)
merged.drop(merged[merged['COMMODITY_DESC']=='GASOLINE-REG UNLEADED'].index, axis=0, inplace=True)


### `COMMODITY_DESC` -> `Section Labels` MAP
# Add section labels
with open('Section_Labels.txt', 'r') as f:
    product_section_map = eval(f.readlines()[0])
ser = merged['COMMODITY_DESC'].map(product_section_map) # hardcoded;
ser = ser.fillna('misc') # for exceptions ?
merged['Section Labels'] = ser


# Remove one-day transactions -- outliers?
def one_day_transactions(df) -> list:
    no_days = df.groupby('household_key').agg({'DAY':'nunique'})
    return list(no_days[no_days['DAY'] == 1].index)

# remove households with only 1 day of purchases;
merged = merged[~merged['household_key'].isin(one_day_transactions(merged))]    


# write data using pandas (for now)
# merged.to_sql(name='_merged_no_hh',
#             con=_SQLALCHEMY_DATABASE_URL,
#             # if_exists='append',
#            if_exists='replace',
#             chunksize=999,
#             method='multi')


# HouseHold Analytics Basic Pivot

### Creating Customer-Level Sales by Section Labels
section_dummies = pd.get_dummies(merged['Section Labels'])
#print(section_dummies.sum().sum())
# the transaction-level (item) binary flags for
#section_dummies.sum()

### total sales by section, for each household
### may want to break this out further, into ie. weekly, bi-weekly, monthly, or quarterly sales totals for each section
section_sales = section_dummies.apply(lambda x : x * merged['SALES_VALUE'])
hh_agg = section_sales.join(merged['household_key']).groupby('household_key').agg({col:'sum' for col in section_dummies.columns})

hh_agg['total_sales'] = hh_agg.sum(axis=1)



# ADDING RFM SCORE
last_days = merged.groupby('household_key')['DAY'].max()
R = pd.cut(last_days, [0, 525, 615, 675, 700, np.inf], labels=[1,2,3,4,5], ordered=True).astype('int')
num_baskets = merged.groupby('household_key')['BASKET_ID'].nunique()
grouper = merged.groupby('household_key')['DAY']
days_in_data = grouper.max() - grouper.min() + 1 #(no day 0 in our data)
transactions_per_day = num_baskets/days_in_data
F = pd.qcut(transactions_per_day, 5, labels=[1,2,3,4,5]).astype('int')
M = pd.qcut(np.log(merged.groupby('household_key')['SALES_VALUE'].sum()), 5, labels=[1,2,3,4,5]).astype('int')
temp = pd.concat([R, F, M], axis=1)
temp.columns = ['r_score', 'f_score', 'm_score']
temp['rfm_score'] = temp.sum(axis=1).astype(int)
customer_ranks = pd.cut(temp['rfm_score'], bins=[0,6,9,13,15, np.inf], labels=[1,2,3,4,5], right=False).astype(int)
customer_ranks = pd.DataFrame(customer_ranks) ## THIS IS HACKY BRO
temp['rfm_bins'] = customer_ranks
hh_agg = temp.merge(hh_agg, on='household_key').reset_index()





# ADD DEMOGRAPHIC DATA TO SUMMARY
demo = a.get_table('hh_demographic')
#pd.read_csv('../data/hh_demographic.csv')
## Alternate Mappings
demo['age_45_plus'] = demo['AGE_DESC'].map({ '19-24':0,
                                        '25-34':0,
                                        "35-44":0,
                                        '45-54':1,
                                        '55-64':1,
                                        '65+':1,
                                        })


demo['income_50K_plus'] = demo['INCOME_DESC'].map({
                        'Under 15K': 0,
                            '15-24K': 0,
                            '25-34K': 0,
                            '35-49K': 0,
                            '50-74K': 1,
                            '75-99K': 1,
                            '100-124K': 1,
                            '125-149K': 1,
                            '150-174K': 1,                   
                            '175-199K': 1,  
                            '200-249K': 1,
                            '250K+': 1,
                        })

# leaving household_size desc IN as a category; single, couple, 3+
demo['single_couple_family'] = demo['HOUSEHOLD_SIZE_DESC'].map({'1':1, '2':2, '3':3,'4':3,'5+':3})
#demo['single_couple_family'] = pd.Categorical(demo['single_couple_family'], 
#                                                [1,2,3,])

demo['has_kids'] = np.where((demo['HH_COMP_DESC'] == '1 Adult Kids') |
                            (demo['HH_COMP_DESC'] == '2 Adults Kids') |
                            (demo['HOUSEHOLD_SIZE_DESC'].isin(['3', '4', '5+'])),
                            1, 0)

demo['single'] =  np.where((demo['HH_COMP_DESC'] == 'Single Female') |
                            (demo['HH_COMP_DESC'] == 'Single Male') |
                            (demo['HOUSEHOLD_SIZE_DESC'] == '1'),
                            1, 0)

demo['couple'] =  np.where((demo['HH_COMP_DESC'] == '2 Adults No Kids'),
                            1, 0)

demo = demo.drop(['AGE_DESC', 'MARITAL_STATUS_CODE', 
            'INCOME_DESC', 'HOMEOWNER_DESC', 'HH_COMP_DESC', 
            'HOUSEHOLD_SIZE_DESC', 'KID_CATEGORY_DESC'], axis=1)


# binary flags for low and high income; low and high age; based on distributions of values in a known data set?
hh_summary = demo.merge(hh_agg, on='household_key')

#hh_summary
### HH_SUMMARY OUTPUT

# to db
hh_summary.set_index('index', inplace=True)
hh_summary.to_sql(name='hh_summary',
                con=_SQLALCHEMY_DATABASE_URL,
            #      if_exists='append',
                if_exists='replace',
                #chunksize=999,
                method='multi')

# to data storage?
# hh_summary.to_csv('data/hh_summary.csv')


### DAILY SPEND BY HOUSEHOLD


# HouseHold Analytics Pivot

### Creating Customer-Level Sales by Section Labels
section_dummies = pd.get_dummies(merged['Section Labels'])
#print(section_dummies.sum().sum())
# the transaction-level (item) binary flags for
#section_dummies.sum()

### total sales by section, for each household
### may want to break this out further, into ie. weekly, bi-weekly, monthly, or quarterly sales totals for each section
section_sales = section_dummies.apply(lambda x : x * merged['SALES_VALUE'])
daily_hh_spend_by_section = section_sales.join(merged[['household_key', 'DAY',]])

daily_hh_spend_by_section =daily_hh_spend_by_section.groupby(['DAY','household_key', ]).agg({col:'sum' for col in section_dummies.columns})

daily_hh_spend_by_section['total_sales'] = daily_hh_spend_by_section.sum(axis=1)


### UNCOMMENT TO RUN


# daily_hh_spend_by_section.to_csv('data/daily_hh_spend_by_section.csv')

# daily_hh_spend_by_section.to_sql(name='daily_hh_spend',
#             con=_SQLALCHEMY_DATABASE_URL,
#             # if_exists='append',
#            if_exists='replace',
#             chunksize=999,
#             method='multi')
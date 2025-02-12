import pandas as pd
from datetime import datetime


df = pd.read_csv('C:/Users/derrick.odonnell/Scripts/netsuite compare/weeklycharge/ts2024.csv', header=0, dtype={'Project Name': 'string'})


'''
print(df.head)
print(df.columns)

df['Project Name'] = df['Project Name'].astype(str)

print(df[['Project Name', 'Amount', 'Date']].head())
'''

print(df.columns)

df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

df['Amount'] = df['Amount'].replace({'\$': '', ',': ''}, regex=True).astype(float)
df['Hours'] = df['Hours'].astype(float)

def get_week_start(date):
    return date - pd.Timedelta(days=(date.weekday() + 1) % 7)

df['Week Start'] = df['Date'].apply(get_week_start)

df['Project Name'] = df['Project Name'].astype(str)


weekly_sums = df.groupby(['Week Start', 'Project Name'])[['Amount','Hours']].sum().reset_index()
weekly_sums = weekly_sums.sort_values(by='Week Start')

#weekly_sums = df.groupby(['Week Start'])[['Amount','Hours']].sum().reset_index()
#weekly_sums = weekly_sums.sort_values(by='Week Start')

#weekly_sums = df.groupby(['Project Name'])[['Amount','Hours']].sum().reset_index()
#weekly_sums = weekly_sums.sort_values(by='Project Name')



print("Weekly Charge Sums:")
for index, row in weekly_sums.iterrows():
    week_end = row['Week Start'] + pd.Timedelta(days=6)  # Ending on Saturday
    print(f"Projects: {row['Project Name']}, Week Start: {row['Week Start'].strftime('%m/%d/%Y')}, Total Charges: ${row['Amount']:.2f}, Total Hours: {row['Hours']}")
    #print(f"Week Start: {row['Week Start'].strftime('%m/%d/%Y')}, Total Charges: ${row['Amount']:.2f}, Total Hours: {row['Hours']}")
    #print(f"Projects: {row['Project Name']}, Total Charges: ${row['Amount']:.2f}, Total Hours: {row['Hours']}")

weekly_sums.to_excel('TS_2024_4.xlsx', index=False)


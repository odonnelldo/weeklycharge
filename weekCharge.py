import pandas as pd
from datetime import datetime


df = pd.read_csv('C:/Users/derrick.odonnell/Scripts/weeklychargesum/brp.csv')

df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

df['Amount'] = df['Amount'].replace({'\$': '', ',': ''}, regex=True).astype(float)

def get_week_start(date):
    return date - pd.Timedelta(days=(date.weekday() + 1) % 7)

df['Week Start'] = df['Date'].apply(get_week_start)

weekly_sums = df.groupby('Week Start')['Amount'].sum().reset_index()

print("Weekly Charge Sums:")
for index, row in weekly_sums.iterrows():
    week_end = row['Week Start'] + pd.Timedelta(days=6)  # Ending on Saturday
    #print(f"{week_end.strftime('%m/%d/%Y')} {row['Amount']:.2f}")
    print(f"Week: {row['Week Start'].strftime('%m/%d/%Y')} - {week_end.strftime('%m/%d/%Y')}, Total Charges: ${row['Amount']:.2f}")
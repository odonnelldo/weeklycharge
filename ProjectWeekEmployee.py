import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.styles import NamedStyle

from datetime import datetime

# Load CSV
df = pd.read_csv('C:/Users/derrick.odonnell/Scripts/netsuite compare/weeklycharge/ts2024.csv')

# Standardize column names (remove extra spaces)
df.columns = df.columns.str.strip()

# Ensure required columns exist
required_columns = ['Project Name', 'Hours', 'Amount', 'Date']
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found! Check CSV formatting!")

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')

# Convert Amount and Hours columns to appropriate types
df['Amount'] = df['Amount'].replace({'\$': '', ',': ''}, regex=True).astype(float)
df['Hours'] = df['Hours'].astype(float)

# Extract only the main project name (before ":")
df['Project Name'] = df['Project Name'].astype(str).str.split(':').str[0].str.strip()

# Function to calculate Week Start (Sunday)
def get_week_start(date):
    return date - pd.Timedelta(days=(date.weekday() + 1) % 7)

df['Week Start'] = df['Date'].apply(get_week_start)

#Filter out rows where "Hours" > 0
df = df[df['Hours'] > 0]

#Group by Week Start & Project Name, summing Amount and Hours
weekly_sums = df.groupby(['Week Start', 'Project Name'])[['Amount', 'Hours']].sum().reset_index()

#Calculate Weekly Totals
weekly_totals = weekly_sums.groupby('Week Start')[['Amount', 'Hours']].sum().reset_index()
weekly_totals['Project Name'] = 'TOTAL'  # Label total row

# Concatenate and sort the DataFrame
final_output = pd.concat([weekly_sums, weekly_totals], ignore_index=False).sort_values(by=['Week Start', 'Project Name'])

# Create a copy of the DataFrame for Excel output
excel_output = final_output.copy()

# Set "Week Start" to empty for "TOTAL" rows in the copy
excel_output.loc[excel_output['Project Name'] == 'TOTAL', 'Week Start'] = ''

# Save to Excel with Formatting
excel_filename = 'weekly_charge_summary_fixed4.xlsx'
with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
    excel_output.to_excel(writer, sheet_name='Weekly Summary', index=False)

    # Auto-adjust column widths
    workbook = writer.book
    worksheet = writer.sheets['Weekly Summary']

    bold_format = workbook.add_format({'bold': True})


    worksheet.set_column('A:A', 25)  # Week Start
    worksheet.set_column('B:B', 40)  # Project Name
    worksheet.set_column('C:C', 15)  # Amount
    worksheet.set_column('D:D', 15)  # Hours


workbook = load_workbook(excel_filename)
sheet = workbook['Weekly Summary']

# Identify rows with "Total" in the "Project Name" column
total_rows = []
for row_idx, row in enumerate(sheet.iter_rows(min_row=2, max_col=2, values_only=True), start=2):
    if row[1] == 'TOTAL':  # "Project Name" is the second column (index 1)
        total_rows.append(row_idx)

# Step 3: Reopen the Excel file with xlsxwriter to apply formatting
with pd.ExcelWriter(excel_filename, engine='openpyxl', mode='a') as writer:
    workbook = writer.book
    worksheet = writer.sheets['Weekly Summary']

    bold_format = Font(bold=True)

    date_style = NamedStyle(name="date_style")
    date_style.number_format = "MM/DD/YYYY"

    # Apply the format to the entire column (assuming column A has dates)
    for cell in worksheet["A"]:  # Change "A" to the actual column letter
        cell.style = date_style


    # Apply bold formatting to identified rows
    for x in total_rows:
        for cell in worksheet[x]:
            cell.font = Font(bold=True)

print(f"✅ Excel file '{excel_filename}' has been saved successfully with totals after each week!")

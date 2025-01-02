import pandas as pd
import pyodbc
from dotenv import dotenv_values
from utils import tweak_attend, tweak_attend_flex, tweak_attend_middle
from datetime import datetime

secrets = dotenv_values(".env")

username = secrets["SQLUSERNAME"]
password = secrets["SQLPASSWORD"]
database = secrets["SQLDATABASE"]
server = secrets["SQLSERVER"]

cnxn = pyodbc.connect(
    """Driver={SQL Server Native Client 11.0};
                      SERVER="""
    + server
    + ";"
    + "DATABASE="
    + database
    + ";"
    + "UID="
    + username
    + ";PWD="
    + password
)

dates_query = """
SELECT 
	DATEADD(DAY, -((DATEPART(WEEKDAY, GETDATE()) + 5) % 7 + 7), CAST(GETDATE() AS DATE)) AS MostRecentMonday,
	DATEADD(DAY, -((DATEPART(WEEKDAY, GETDATE()) + 1) % 7), CAST(GETDATE() AS DATE)) AS MostRecentFriday;
"""
dates_df = pd.read_sql_query(dates_query, cnxn)
print(dates_df)

# ------------------------------------
# School 68 - query 1 - just all day codes
with open("StudentsAbsencesDaterange.sql", "r") as file:
    query1 = file.read()

df = pd.read_sql_query(query1, cnxn)
dfs = {"School 68 - Special Services": tweak_attend(df)}

# ------------------------------------
# School 6* - query 2 - period codes in ATT table
with open("StudentsAbsencesMIDDLEDaterange.sql", "r") as file:
    query2 = file.read()

df = pd.read_sql_query(query2, cnxn)
dfs["School 69 - Special Middle"] = tweak_attend_middle(df)

# ------------------------------------
# School 70 - query 3 - CAT table period codes
with open("StudentsAbsencesFLEXDaterange.sql", "r") as file:
    query3 = file.read()

df = pd.read_sql_query(query3, cnxn)
dfs["School 70 - Special High"] = tweak_attend_flex(df)

# ------------------------------------
# School 72 - query 3 - CAT table period codes
query3 = query3.replace(
    "CAT.SCL = 70", "CAT.SCL = 72"
)  # school 70 and 72 have flex scheduling
df = pd.read_sql_query(query3, cnxn)
dfs["School 72 - Special High - UMHS"] = tweak_attend_flex(df)

# ------------------------------------
# School 73 - query 1 - just all day codes
query1 = query1.replace(
    "STU.SC = 68", "STU.SC = 73"
)  # school 68 and 73 have all day absence codes.
df = pd.read_sql_query(query1, cnxn)
dfs["School 73 - Adult Transition"] = tweak_attend(df)


# Write to Excel
index_needed = dict(zip(dfs.keys(), [False, False, True, True, False]))
now = datetime.now()
output_path = f"weekly_attendance_report_{dates_df.iloc[0,0]}_thru_{dates_df.iloc[0,1]}_runtime-{now.strftime("%m-%d-%Y %H.%M.%S")}.xlsx"
with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    for sheet_name, df in dfs.items():
        df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=index_needed[sheet_name],
            startrow=0,
        )
        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # Add a table format
        # num_rows, num_cols = df.shape
        # column_settings = [{'header': column} for column in df.columns]
        # worksheet.add_table(0, 0, num_rows, num_cols - 1, {
        #     'columns': column_settings,
        #     'style': 'Table Style Medium 9',  # Excel Table Style
        # })

        if not index_needed[sheet_name]:
            # Autofit columns
            for col_num, value in enumerate(df.columns):
                column_width = max(len(value), df[value].astype(str).map(len).max()) + 2
                worksheet.set_column(col_num, col_num, column_width)

        if index_needed[sheet_name]:
            # Autofit columns (including index)
            df_reset = df.reset_index()  # Include index as a column
            for col_num, column_name in enumerate(df_reset.columns):
                max_content_length = max(
                    len(str(column_name)),  # Header length
                    df_reset[column_name].astype(str).map(len).max(),  # Content length
                )
                worksheet.set_column(col_num, col_num, max_content_length + 2)


print(f"DataFrames saved to {output_path}")
input("press enter to close")

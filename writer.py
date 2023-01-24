import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from tornado import concurrent

from timer import timer

load_dotenv()

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scopes=scope
)
client = gspread.authorize(credentials)


def write_df_to_sheet(sheet_name, df):
    sheet = client.create(sheet_name)
    worksheet = client.open(sheet_name).sheet1
    sheet.share(os.getenv("SHARE_EMAIL"), perm_type="user", role="writer")
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())


def write_picked_df_to_sheet(worksheet, df, name):
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print(f"Done({name})", end=" ")


@timer
def write_dataframes_to_sheets(sheet_name, grouped_dataframes):
    sheet = client.create(sheet_name)
    sheet.share(os.getenv("SHARE_EMAIL"), perm_type="user", role="writer")
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for name, df in grouped_dataframes:
            print(name, end=" ")
            df = df[:30_000]
            worksheet = sheet.add_worksheet(
                title=name,
                rows=len(df),
                cols=len(df.columns)
            )
            futures.append(
                executor.submit(
                    write_picked_df_to_sheet,
                    worksheet,
                    df,
                    name
                )
            )
        executor.shutdown()

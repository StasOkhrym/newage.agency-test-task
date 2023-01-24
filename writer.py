import os

import gspread
from dotenv import load_dotenv
from gspread import Worksheet
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy
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


def write_df_to_sheet(sheet_name: str, df: DataFrame) -> None:
    sheet = client.create(sheet_name)
    worksheet = client.open(sheet_name).sheet1
    sheet.share(os.getenv("SHARE_EMAIL"), perm_type="user", role="writer")
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())


def write_picked_df_to_sheet(worksheet: Worksheet, df: DataFrame, name: str) -> None:
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    print(f"Done({name})", end=" ")


@timer
def write_dataframes_to_sheets(
    sheet_name: str, grouped_dataframes: DataFrameGroupBy
) -> None:
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

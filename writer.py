import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials


load_dotenv()

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

basedir = os.path.abspath(__file__)
data_json = os.path.join(basedir + "credentials.json")

credentials = ServiceAccountCredentials.from_json_keyfile_name(data_json, scopes=scope)
client = gspread.authorize(credentials)


def write_df_to_sheet(sheet_name, dataframe):
    sheet = client.create(sheet_name)
    worksheet = client.open(sheet_name).sheet1
    sheet.share("SHARE_EMAIL", perm_type="user", role="writer")
    worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

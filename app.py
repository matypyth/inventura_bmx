from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os

app = Flask(__name__, template_folder="INVENTORY_BMX/templates")

ITEM_NAMES = [f"item_{i}" for i in range(21)]  # 0 - 20


def get_spreadsheet():
    # Definuj cestu k súboru v Render Secrets
    credentials_path = '/etc/secrets/week-inventory-4667af524caa.json'

    # Skontroluj, či súbor existuje na správnom mieste
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Súbor s credentials neexistuje na ceste {credentials_path}")

    # Definuj rozsah oprávnení
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Načítanie credentials zo súboru
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

    # Autorizácia a prístup do spreadsheetu
    client = gspread.authorize(creds)
    
    try:
        spreadsheet = client.open("Inventura2025")
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create("Inventura2025")
        spreadsheet.share('sklad401@week-inventory.iam.gserviceaccount.com', perm_type='user', role='writer')

    spreadsheet.share('martinkopythonko@gmail.com', perm_type='user', role='writer')
    return spreadsheet


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = []
        for name in ITEM_NAMES:
            value = request.form.get(name, "")
            data.append([name, value])

        spreadsheet = get_spreadsheet()
        existing_titles = [ws.title for ws in spreadsheet.worksheets()]
        max_number = -1
        for title in existing_titles:
            if title.startswith("Inventura"):
                try:
                    number = int(title.replace("Inventura", ""))
                    max_number = max(max_number, number)
                except ValueError:
                    continue

        new_sheet_name = f"Inventura{max_number + 1}"
        sheet = spreadsheet.add_worksheet(title=new_sheet_name, rows=100, cols=20)

        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        sheet.update_cell(1, 1, f"Dátum: {current_date}")
        sheet.append_row(["Položka", "Množstvo"])
        for row in data:
            sheet.append_row(row)

        return redirect("/")

    return render_template("index.html", items=ITEM_NAMES)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

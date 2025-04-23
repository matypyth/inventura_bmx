from flask import Flask, render_template, request, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os

app = Flask(__name__, template_folder="INVENTORY_BMX/templates")

# Pevne dané názvy položiek a ID položiek
ITEMS = [
    {"id": "100038", "name": "Lepiaca páska obojstranná 2,5cm"},
    {"id": "100010", "name": "GAS TAPE -1 krabica -48ks kotuc x 50m"},
    {"id": "100030", "name": "Lepiaca paska transp.ručná"},
    {"id": "100039", "name": "Lepiaca paska transp.strojová"},
    {"id": "RT/5011/1", "name": "Lepiaca paska papierová"},
    {"id": "22310", "name": "Ručna folia"},
    {"id": "0.022300", "name": "Strojov folia (1plt-24ks/alebo 28ks -cca na 4mes.)"},
    {"id": "100055", "name": "Návleky modre XCM036 protismykove (incl. 1000pcs/wk/ART)"},
    {"id": "6352", "name": "čiapky skladačka biela (incl. 350pcs ART)"},
    {"id": "", "name": "sietky na bradu"},
    {"id": "", "name": "jednorázové kukly - astro cap / mask"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex MA-144-XS00-018"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex S MA-144-S000-018"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex M MA-144-M00-018"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex L MA-144-L000-018"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex XL MA-144-XL00-018"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex XS - modré MA-144-XS00-020"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex S - modré MA-144-S000-020"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex M - modré MA-144-M00-020"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex L - modré MA-144-L000-020"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex XL - modré MA-144-XL00-020"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex XS - fialove MA-144-XS00-021"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex S - fialove MA-144-S000-021"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex M - fialove MA-144-M00-021"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex L - fialove MA-144-L000-021"},
    {"id": "RT-200/0", "name": "Rukavice Ambulex XL -fialove MA-144-XL00-021"},
    {"id": "0.000601", "name": "Náprstky M"},
    {"id": "", "name": "Náprstky L"},
    {"id": "", "name": "Náprstky XL"},
    {"id": "111181", "name": "DYMAX UV glue 1ks-1l (max zasoba 10l)"},
    {"id": "100017", "name": "THF Tetrahydrofuran 1ks-1l (max zasoba 20l)"},
    {"id": "100002", "name": "Cyclohexanone 1ks-1l (max zasoba 20l)"},
    {"id": "RT/5185/4", "name": "T-200-9000 Pad printer black ink"},
    {"id": "RT/5185/5", "name": "100-VR-1433 Hardener printing machine 1ks-100ml"},
    {"id": "RT/5185/6", "name": "38571 Thinner fast printing machine 1ks-1l"},
    {"id": "RT/5185/7", "name": "35928 Retarder printing machine 1ks-1l"},
    {"id": "RT/200-0", "name": "Epson TM-C7500G SJIC30P(Y)C33S020642 yellow ink"},
    {"id": "RT/200-0", "name": "Epson TM-C7500G SJIC30P(K)C33S020639 black ink"},
    {"id": "RT/200-0", "name": "Epson TM-C7500G SJIC30P(M)C33S020641 magenta ink"},
    {"id": "RT/200-0", "name": "Epson TM-C7500G SJIC30P(C)C33S020640 cyan ink"},
    {"id": "C33S020596", "name": "Maintenance Box for EPSON"},
    {"id": "RT-200-0", "name": "Utierky pre BMX (1bal/150ks)"},
    {"id": "000898AR", "name": "RBN ZEBRA 3200 Resign 110x300m"},
    {"id": "21211 / GN900-300", "name": "Sticky matts lepiace podložky (10 pcs/ box) incl. ART 2ks/mes"},
    {"id": "F005-SK", "name": "Tlačivo ID final Product Tracing"},
    {"id": "F004-SK", "name": "Tlačivo ID final Product Tracing"},
    {"id": "RT/5011/1", "name": "Mikrotenové sačky 30x40"},
    {"id": "RT/5011/2", "name": "Sačky 500x700 1bal-500ks"},
    {"id": "8LS060", "name": "Sáčky 500x600 (iba 401) 1krt-500ks"},
    {"id": "RT/5011/3", "name": "LDPE 700x1100x0.04 1bal-250ks HDPE Vrolo 700x1100x0,023 trsp (náhrada za 8LS055)"},
    {"id": "8LS055", "name": "Sačky 700x1100x0.02 transp. (iba 401) 1krt-500ks"},
    {"id": "RT-200//0", "name": "TTR RIBBON R230 110X450M (blue)"},
    {"id": "RT/5011/1", "name": "Ribbon Zebra 110x74m čierná"},
    {"id": "100011", "name": "Chemical indicator"},
    {"id": "100300", "name": "etiketa prepravne znaky et.75x300 cca 5000ks-1krt"},
    {"id": "100221", "name": "Label Nonstandard Quantity -info od QC"},
    {"id": "100270", "name": "Label white 92x103mm 1kotuc-1000ks"},
    {"id": "0.000301", "name": "Label MRB 50x25mm 1kotuc-1000ks"},
    {"id": "0.000302", "name": "Label GOOD 50x25mm 1 kotuc-1000ks"},
    {"id": "0.000303", "name": "Label REJECT 1kotuc-1000ks"},
    {"id": "RT/5014/1", "name": "Status Reject 68x38mm"},
    {"id": "0.000307", "name": "Status GOOD 68x38mm mala dutinka 1kotuc-2000ks"},
    {"id": "0.000308", "name": "Status MRB 68x38mm mala dutinka 1kotuc-2000ks"},
    {"id": "RT-200/0", "name": "Label QC final inspection (3-4cm x7cm) - nepoužívame (Y-connectory)"},
    {"id": "RT-200/0", "name": "Label QC LAL Test (3-4cm x7cm) - nepoužívame Y-connectory"},
    {"id": "8CR050", "name": "Rohy na palaty"},
    {"id": "22314", "name": "Palety 120x80 jednocestné"},
    {"id": "", "name": "Euro palety SVETLE / TMAVE"},
    {"id": "", "name": "PLASTOVE PALETY"},
    {"id": "8CR009 1/2", "name": "Carton Sleeve 172X206 NELEPENÉ"},
    {"id": "8CR009 1", "name": "Carton Sleeve 800X1200X1800cm LEPENÉ"},
    {"id": "8CR010", "name": "Carton 248x108x220mm,White Printed"},
    {"id": "8CR020", "name": "Carton Cover 200x500mm"},
    {"id": "8CR090", "name": "Carton 1195x221x138"},
    {"id": "8CR094", "name": "Carton1192x192x82mm"},
    {"id": "8CR095", "name": "Carton 392x232x160mm"},
    {"id": "8CR097", "name": "Carton 310x105x135mm"},
    {"id": "8CR100", "name": "Carton 267x252x126mm"},
    {"id": "8CR101", "name": "Carton 786x286x275mm"},
    {"id": "8CR102", "name": "Carton 385x284x183mm"},
    {"id": "8CR103", "name": "Carton 775x380x412mm"},
    {"id": "8CR104", "name": "Carton 787x189x131 mm"},
    {"id": "8CR107", "name": "Carton 557X227X230mm"},
    {"id": "8CR115", "name": "Carton388X388X286mm"},
    {"id": "8CR124", "name": "Carton 745X580X358 mm"},
    {"id": "8CR201", "name": "Carton 780X380X260 mm"},
    {"id": "8CR302", "name": "Carton 390X288X238 mm"},
    {"id": "8CR304", "name": "Carton 590X390X277 mm"},
    {"id": "8CR332", "name": "Carton 392X288X400mm"},
    {"id": "8CR501", "name": "Box 170x220x80mm"},
    {"id": "8CR502", "name": "Box 410x345x225mm"},
    {"id": "8CR504", "name": "Carton Spacer 750x1150mm"},
    {"id": "8CR150", "name": "Carton 387x387xs417 mm"},
    {"id": "8CR111", "name": "Carton 372x183x204 mm"},
    {"id": "8CR114", "name": "Carton 368x186x115mm"},
    {"id": "8CR120", "name": "Carton 554x258x60mm"},
    {"id": "0.05020006", "name": ""},
    {"id": "0.05020003", "name": ""},
    {"id": "8CR308", "name": ""},
    {"id": "8CR234", "name": ""},
    {"id": "8CR503", "name": ""},
    {"id": "8CR507", "name": ""},
    {"id": "8CR508", "name": ""},
    {"id": "8CR506", "name": ""}
]

CHEMICAL_ITEMS = [
  {"id": "Vidra", "name": "INCIDIN OXYFOAM S 750ml"},
  {"id": "Vidra", "name": "DESPREJ 5l"},
  {"id": "Vidra", "name": "DESPREJ 500 ml"},
  {"id": "Vidra", "name": "SKINMAN SOFT PROTECT 1l (na dezinkfeciu rúk)"},
  {"id": "Vidra", "name": "Mitia 1 l"},
  {"id": "Vidra", "name": "Surfanios Premium 5 l"},
  {"id": "Vidra", "name": "SILONDA 500ml (krém na ruky)"},
  {"id": "Infolab", "name": "Dezix 5l (na dezinfeciu rúk)"},
  {"id": "Vidra", "name": "CHEMISEPT GEL 1l (na dezinkfeciu rúk)"},
  {"id": "Vidra", "name": "CHEMISEPT GEL 5l (na dezinkfeciu rúk)"},
  {"id": "St. Nicolaus", "name": "Killvir 5l (na dezinkfeciu rúk)"},
  {"id": "Vidra", "name": "Bacticid AF 5L /náhrada za Despej"},
  {"id": "Vidra", "name": "BActicid AF (Vlhké utierky)"},
  {"id": "Vidra", "name": "Sterisept 1L - náhrada za Oxyfoam"}
]

def get_spreadsheet():
    credentials_path = '/etc/secrets/week-inventory-4667af524caa.json'

    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Súbor s credentials neexistuje na ceste {credentials_path}")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)

    try:
        spreadsheet = client.open("Inventura2025")
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create("Inventura2025")
        spreadsheet.share('sklad401@week-inventory.iam.gserviceaccount.com', perm_type='user', role='writer')

    spreadsheet.share('martinkopythonko@gmail.com', perm_type='user', role='writer')
    return spreadsheet


def create_inventory_sheet(spreadsheet, base_name, data):
    existing_titles = [ws.title for ws in spreadsheet.worksheets()]
    max_number = 0
    for title in existing_titles:
        if title.startswith(base_name):
            try:
                number = int(title.replace(base_name, "").strip("_"))
                max_number = max(max_number, number)
            except ValueError:
                continue

    new_sheet_name = f"{base_name}_{max_number + 1}"
    sheet = spreadsheet.add_worksheet(title=new_sheet_name, rows=100, cols=3)

    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    
    # Zápis dátumu do A1 – POZOR: dvojrozmerné pole
    sheet.update("A1", [[f"Dátum: {current_date}"]])
    
    # Hlavička + dáta
    header = [["ID POLOŽKY", "NÁZOV POLOŽKY", "MNOŽSTVO"]]
    all_data = header + data

    # Zápis všetkých dát naraz
    sheet.append_rows(all_data, value_input_option="USER_ENTERED")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = []
        for item in ITEMS:
            input_id = item['name'].replace(" ", "_").replace(",", "").replace(".", "").lower()
            raw_quantity = request.form.get(f"quantity_{input_id}", "").replace(",", ".")
            try:
                quantity = float(raw_quantity)
                data.append([item.get('id', ''), item['name'], quantity])
            except ValueError:
                data.append([item.get('id', ''), item['name'], ""])  # prázdne ak neplatné

        spreadsheet = get_spreadsheet()
        create_inventory_sheet(spreadsheet, "Inventura", data)

        return redirect("/")

    return render_template("index.html", items=ITEMS, page="main")


@app.route("/dezinfekcia", methods=["GET", "POST"])
def dezinfekcia():
    if request.method == "POST":
        data = []
        for item in CHEMICAL_ITEMS:
            input_id = item['name'].replace(" ", "_").replace(",", "").replace(".", "").lower()
            raw_quantity = request.form.get(f"quantity_{input_id}", "").replace(",", ".")
            try:
                quantity = float(raw_quantity)
                data.append([item.get('id', ''), item['name'], quantity])
            except ValueError:
                data.append([item.get('id', ''), item['name'], ""])

        spreadsheet = get_spreadsheet()
        create_inventory_sheet(spreadsheet, "Inventura_dezinfekcia", data)

        return redirect("/dezinfekcia")

    return render_template("index.html", items=CHEMICAL_ITEMS, page="dezinfekcia")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)

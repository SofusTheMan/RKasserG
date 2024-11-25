import pdfplumber
import pandas as pd
import sys
import re


def from_danish(number_str):
    """Convert a Danish number format string to a float."""
    return float(number_str.replace('.', '').replace(',', '.'))

def check_carls(lines):
    mixer = ["Coca-Cola", "Fanta", "Schweppes", "Craft"]
    cider = fustage = flaske = vand = energi = pant = 0.0 


    for l in lines:
        parts = l.split()
        #print(parts)
        if any(p == "Somersby" for p in parts):
            cider += from_danish(parts[len(parts)-2])
        if any(p == "Tuborg" or p == "Blanc" for p in parts):
            if any(p == "fustage" for p in parts):
                fustage += from_danish(parts[len(parts)-2])
                print(fustage)
            elif any(p == "flaske," for p in parts):
                flaske += from_danish(parts[len(parts)-2])
        if any(p in mixer for p in parts):
            vand += from_danish(parts[len(parts)-2])
        if any(p == "Monster" for p in parts):
            energi += from_danish(parts[len(parts)-2])
        if "Subtotal" in parts and "emballage" in parts:
            pant = from_danish(parts[len(parts)-2])
    

    total = cider + flaske + fustage + vand + energi + pant 
    bilag = [['Cider', cider*1.25], ['Øl', flaske*1.25], ['fustage', fustage*1.25],['Vand', vand*1.25],
             ['Energi', energi*1.25], ['Pant', pant*1.25], ['Total', total * 1.25]]
    return bilag

def check_drinx(lines):
    other = ["Pant", "Palle"]
    mixer = ["Maté", "Sprite", "Schweppes"]
    booze = ["Vodka", "Baileys", "Gammel", "Bacardi", "Fugle", "Cuba", "Jägermeister#", "Gin", "Fernet-Branca"]
    fustage = cider = tilbehør = spiritus = vand = energi = pant = 0.0 

    for l in lines:
        parts = l.split()
        if any(p in booze for p in parts):
            spiritus += from_danish(parts[len(parts)-1])
        if any(p in mixer for p in parts):
            vand += from_danish(parts[len(parts)-1])
        if any(p in other for p in parts):
            pant += from_danish(parts[len(parts)-1])
        if "Red" in parts and "Bull" in parts:
            energi += from_danish(parts[len(parts)-1])
        if any(p == "Istønde," for p in parts):
            tilbehør += from_danish(parts[len(parts)-1])
        if "Fustage" in parts and "Pant" not in parts:
            fustage += from_danish(parts[len(parts)-1])
        if any(p == "Ice" for p in parts):
            cider += from_danish(parts[len(parts)-1])

    total = tilbehør + spiritus + vand + energi + pant + fustage + cider
    bilag = [['Tilbehør', tilbehør*1.25],['Spiritus', spiritus*1.25], ['Vand', vand*1.25],
             ['Energi', energi*1.25], ['Pant', pant*1.25],['Cider', cider*1.25], 
             ['Fadøl', fustage*1.25],['Total', total*1.25]]
    return bilag


def pdf_to_csv(pdfFile, output, arg):
    #flaske, fustage, cider, spiritus, pant, energi = 0.0
    with pdfplumber.open(pdfFile) as pdf:
        data = [['Kategori', 'Belød']] 
        for p in pdf.pages:
            text = p.extract_text()
            lines = text.split("\n")
            match arg:
                case "c":
                    out = check_carls(lines)
                    data += [dat for dat in out]
                case "d":
                    out = check_drinx(lines)
                    data += [dat for dat in out]
                case _:
                    print("Type not supported.")
                    return

    frame = pd.DataFrame(data)
    frame.to_csv(output, index=False, header=False) 


if len(sys.argv) < 3 or len(sys.argv) > 3:
    print("Usage: python3 RKasserG.py [bilag type] [file path]")
else:
    place = sys.argv[1]
    file = sys.argv[2]
    output = file.replace(".pdf", ".csv")
    pdf_to_csv(file, output, place)

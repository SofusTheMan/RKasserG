import pdfplumber
import pandas as pd
import sys
import re

def check_carls(lines):
    soda = ["Coca-Cola", "Fanta", "Schweppes", "Craft"]
    cider = fustage = flaske = vand = energi = pant = 0.0 
    for l in lines:
        parts = l.split()
        if any(p == "Sommersby" for p in parts):
            cider += parts[len(parts)-2]
        if any(p == "Tuborg" or p == "Blanc" for p in parts):
            if any(p == "fustage" for p in parts):
                fustage += parts[len(parts)-2]
            else:
                flaske += parts[len(parts)-2]
        if any(p in soda for p in parts):
            vand += parts[len(parts)-2]
        if any(p == "Monster" for p in parts):
            energi += parts[len(parts)-2]
        if any(p == "Subtotal" and p == "emballage" for p in parts):
            pant = parts[len(parts)-2]
    

        bilag = [["Cider", cider*1.25], ["Øl", flaske*1.25], ["fustage", fustage*1.25],
                 ["Vand", vand*1.25], ["Energi", energi*1.25], ["Pant", pant*1.25]]
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
                    data.append(out)
                case "d":
                    out = check_drinx(lines)
                    data.append(out)
                case _:
                    print("Type not supported.")
                    return

    frame = pd.DataFrame(data)
    frame.to_csv(output, index=False, header=False) 


pdf_to_csv("carls.pdf", "carls.csv", "c")

import pdfplumber
import pandas as pd

def pdf_to_csv(pdfFile, output):
    with pdfplumber.open(pdfFile) as pdf:
        data = []
        for p in pdf.pages:
            text = p.extract_text()
            lines = text.split("\n")

            for l in lines:
                if any(char.isdigit() for char in l):
                    parts = l.split()
                    data.append(parts)


    frame = pd.DataFrame(data)
    frame.to_csv(output, index = False, header=False)


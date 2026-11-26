import pdfplumber
import pandas as pd
import sys

def from_danish(number_str):
    """Convert a Danish number format string to a float."""
    return float(number_str.replace('.', '').replace(',', '.'))

def from_danishh(val_str):
    # Konverterer "1.541,19" til 1541.19
    try:
        return float(val_str.replace('.', '').replace(',', '.'))
    except ValueError:
        return 0.0

def check_carls(lines):
    # Definition af regler: Jo mere specifik reglen er, jo tidligere skal den stå
    # Vi bruger tupler af ord, som ALLE skal findes i linjen for et match.
    rules = {
        'Fadøl': [
            ('Modular', 'fustage')
        ],
        'Energi': [
            ('Monster',)
        ],
        'Vand': [
            ('Coca-Cola', 'Original', 'Taste'), 
            ('Coca-Cola', 'Zero', 'Sugar'), 
            ('Schweppes',), 
            ('Sprite',), 
            ('Craft', 'Lemonade'), 
            ('Sparkling',),
            ('Fanta', 'Orange')
        ],
        'Øl': [
            ('Tuborg', 'Classic'), 
            ('Pilsner',), 
            ('Tuborg', 'Guld'), 
            ('Grøn', 'Tuborg',),
            ('Tuborg', 'Påskebryg',),
        ],
        'Cider' : [
            ('Somersby', 'Mango'),
            ('Somersby', 'Blackberry'),
            ('Somersby', 'Elderflower'),
            ('Somersby', 'Apple'),
            ('Somersby', 'Red', 'Orange'),
        ],
        'Pant' : [
            ('Flaskepant',),
            ('FLASKEPANT',),
            ('Euro', '1/2-palle'), 
            ('Euro', '1/1-palle'), 
            ('Draught', 'Master',),
            ('Tuborg', '33', 'cl', 'tom', 'ks'),
            ('Tuborg', '33', 'cl', 'ks'),
            ('25', 'l', 'fustage', 'tom'),
            ('25', 'cl', 'tom', 'ks')
        ],
        'Spiritus' : [
            ('Eristoff', 'Original'),
            ('Aftalerabat', 'LTR'),
            ('Aftalerabat', 'LTR'),
            ('Cazadores', 'Blanco'),
        ],
    }

    totals = {name: 0.0 for name in rules.keys()}
    
    for line in lines:
        if not line.strip(): continue
        
        # Find beløbet (sidste tal før DKK)
        parts = line.split()
        if len(parts) < 2: continue
        
        # Finder det sidste tal i linjen (før "DKK" hvis det findes)
        value_idx = -2 if parts[-1] == 'DKK' else -1
        amount = from_danishh(parts[value_idx])
        
        matched_category = None
        
        # Tjek reglerne én efter én
        for category, sequences in rules.items():
            for seq in sequences:
                # Tjek om alle ord i sekvensen findes i linjen (case-insensitive)
                if all(word in line for word in seq):
                    matched_category = category
                    break
            if matched_category:
                break
        
        if matched_category:
            totals[matched_category] += amount
            print(f"Match: [{matched_category}] -> {line.strip()} ({amount})")
        else:
            print(f"Intet match fundet for: {line.strip()}")

    # Beregn moms (1.25) og lav bilag
    bilag = [[cat, round(amt * 1.25, 2)] for cat, amt in totals.items()]
    total_moms = sum(amt for _, amt in bilag)
    bilag.append(['Total inkl. moms', round(total_moms, 2)])
    
    return bilag

def check_drinx(lines):
    # Definition af regler: Jo mere specifik reglen er, jo tidligere skal den stå.
    # Vi bruger tupler af ord. Alle ord i en tuppel skal findes i linjen for et match.
    rules = {
        'Pant': [
            ('Palle',),
            ('Pant', 'A'),
            ('Pant', 'C', 'm/8'),
            ('Pant', 'Draughtmaster', 'Fustage'),
            ('Pant', 'Tønde'),
            ('Pant', 'Tom', 'Kasse')
        ],
        'Miljøafgift': [
            ('Miljøtillæg',)
        ],
        'Fadøl': [
            # Denne fanger fustager, som ikke er pant (da Pant tjekkes først ovenfor)
            ('Fustage',)
        ],
        'Tilbehør': [
            ('Istønde',), 
            ('Strips',), 
            ('Pantsække',), 
            ('Appelsiner',), 
            ('Istang',), 
            ('Lime',), 
            ('Mynte',), 
            ('Rørsukker',), 
            ('Sugerør',), 
            ('Monin',), 
            ('Ponte',), 
            ('t/fadølsanlæg',),
            ('Barmix', 'Syrup'), 
            ('Bordsalt,', 'Fint'), 
            ('Affaldsæk,'), 
            ('Batteri', 'AA')
        ],
        'Vand': [
            ('Sprite',), ('Schweppes',), ('Faxe', 'Kondi,', 'Dåse', '(24x33cl', '+pant)#'), 
            ('Coca',), ('Pellegrino',), ('Ginger', 'Beer'),
            ('Rynkeby', 'Appelsinjuice')
        ],
        'Spiritus': [
            ('Vodka',), ('Baileys',), ('Gammel',), ('Bacardi',), ('Fugle',), 
            ('Cuba',), ('Jägermeister',), ('Goat', 'Gin',), ('Fernet-Branca',), 
            ('Pisang',), ('Minttu',), ('Aperol',), ('Prosecco',), 
            ('Tequila',), ('Passoa',), ('Råstoff',), ('Sambuca',), ('Havana',)
        ],
        'Energi': [
            ('Maté',), ('Red', 'Bull'), ('Monster',)
        ],
        'Cider': [
            ('Smirnoff', 'Ice',), ('Somersby',)
        ],
        'Øl': [
            ('Ceres',), 
            ('Tuborg', 'Påskebryg',),
            ('Classic',)
        ]
    }

    # Initialiser totaler baseret på reglerne
    totals = {name: 0.0 for name in rules.keys()}
    
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        
        parts = clean_line.split()
        if len(parts) < 1:
            continue
            
        # Finder beløbet (sidste del af linjen)
        try:
            # Bruger from_danish (justér til from_danishh hvis nødvendigt)
            amount = from_danish(parts[-1])
        except (ValueError, IndexError):
            continue
        
        matched_category = None
        
        # Tjek reglerne én efter én (rækkefølgen i 'rules' dikterer prioritet)
        for category, sequences in rules.items():
            for seq in sequences:
                # Tjek om alle ord i sekvensen findes i linjen (case-insensitive)
                if all(word in clean_line for word in seq):
                    matched_category = category
                    break
            if matched_category:
                break
        
        if matched_category:
            totals[matched_category] += amount
            print(f"Match: [{matched_category}] -> {clean_line} ({amount})")
        else:
            print(f"Intet match fundet for: {clean_line}")

    # Beregn moms (1.25) og lav bilag (samme format som før)
    bilag = [[cat, round(amt * 1.25, 2)] for cat, amt in totals.items()]
    
    # Beregn den samlede total inkl. moms
    total_moms = sum(item[1] for item in bilag)
    bilag.append(['Total inkl. moms', round(total_moms, 2)])
    
    return bilag

def check_carls_tilskud(lines):
    # Definition af regler: Jo mere specifik reglen er, jo tidligere skal den stå
    rules = {
        'ØL': [
            ('FL',), ('DS',), ('FL.',), ('Fl',), ('Fl.',)
        ],
        'Cider': [
            ('Cider/Fabs',)
        ],
        'Fadøl': [
            ('Fad',)
        ],
        'Energidrik': [
            ('Energy',)
        ],
        'Vand': [
            ('CL',)
        ],
    }

    totals = {name: 0.0 for name in rules.keys()}

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        parts = clean_line.split()
        if len(parts) < 1:
            continue

        # Beløbet forventes som sidste token
        value_token = parts[-1]

        try:
            amount = from_danish(value_token)
        except (ValueError, IndexError):
            continue

        matched_category = None

        for category, sequences in rules.items():
            for seq in sequences:
                if all(word in clean_line for word in seq):
                    matched_category = category
                    break
            if matched_category:
                break

        if matched_category:
            totals[matched_category] += amount
            print(f"Match: [{matched_category}] -> {clean_line} ({amount})")
        else:
            print(f"Intet match fundet for: {clean_line}")

    bilag = [[cat, round(amt * 1.25, 2)] for cat, amt in totals.items()]
    total_moms = sum(item[1] for item in bilag)
    bilag.append(['Total inkl. moms', round(total_moms, 2)])
    return bilag
def nemlig_bilag(lines):
    # Definition af regler: Jo mere specifik reglen er, jo tidligere skal den stå.
    # Vi bruger tupler af ord, som ALLE skal findes i linjen for et match.
    rules = {
        'Øl': [
            ('Grøn', 'Tuborg'), 
            ('Tuborg', 'Classic'),
        ],
        'Fadøl': [
            ('fustage',)
        ],
        'Cider': [
            ('Somersby',), 
            ('SHAKER', 'Sport'), 
            ('Breezer',)
        ],
        'Spiritus': [
            ('Baileys',), 
            ('Absolut', 'vodka',), 
            ('Små', 'Sure',), 
            ('Casa', 'Nogal'), 
        ],
        'Vand': [
            ('Coca-Cola',), 
            ('Squash',), 
            ('kakaomælk',), 
            ('Faxe', 'Kondi')
        ],
        'Mad': [
            ('Minimælk',),
            ('Kartoffelspegepølse',),
            ('Leverpostej',),
            ('Skrabeæg',),
            ('Smør',),
            ('yoghurt',),
            ('Hamburgerryg',),
            ('Rullepølse',),
            ('Veggie sandwichskiver',),
            ('Bacon',),
            ('Creme fraiche',),
            ('Hummus',),
            ('Smørbar',),
            ('Piskefløde',),
            ('Veggie spegepølse',),
            ('Cocktailpølser',),
            ('Falafel',),
            ('Ost i skiver',),
            ('Mozzarella',),
            ('Kyllingebrystfilet',),
            ('Peberfrugt',),
            ('Banan',),
            ('Æble',),
            ('Agurk',),
            ('Tomat',),
            ('Iceberg salat',),
            ('Løg',),
            ('Champignon',),
            ('Hvidløg',),
            ('Wokblanding',),
            ('Håndværkere',),
            ('Ærter',),
            ('Rundstykker',),
            ('Pålægschokolade',),
            ('Mayonnaise',),
            ('Remoulade',),
            ('Havregryn',),
            ('Solsikkerugbrød',),
            ('Chunky salsa dip',),
            ('Hindbærmarmelade',),
            ('Solbærmarmelade',),
            ('Basilikum',),
            ('Majs',),
            ('Grøn karrypasta',),
            ('Parboiled ris',),
            ('Grøntsagsbouillon',),
            ('Tortilla wraps',),
            ('Kikærter',),
            ('Jalapenos',),
            ('Ristede løg',),
            ('Solsikkeolie',),
            ('Baked beans',),
            ('Løgpulver',),
            ('Kokosmælk',),
            ('BBQ sauce',),
            ('Kaffe',),
            ('Appelsin nektar',),
            ('Æble nektar',),
            ('Panodil',),
            ('Håndsæbe',),
            ('Tandbørste',),
            ('Altmuligklude',),
            ('Rengøringssvampe',),
            ('Køkkenrulle',),
            ('Toiletpapir',),
            ('Fryseposer',),
            ('Opvaskemiddel',),
            ('Bagepapir',),
            ('Gummihandsker',),
            ('Opvaskebørste',),
            ('Affaldssække',),
            ('Viskestykker',),
        ],
        'Pant': [
            ('Pant',)
        ],
        'Fragt': [
            ('Fragt',), ('Pakkegebyr',)
        ],
        'Kortgebyr': [
            ('Kortgebyr',),
        ],
    }

    totals = {name: 0.0 for name in rules.keys()}

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        parts = clean_line.split()
        if len(parts) < 1:
            continue

        try:
            amount = from_danish(parts[-1])
        except (ValueError, IndexError):
            continue

        matched_category = None

        for category, sequences in rules.items():
            for seq in sequences:
                if all(word in clean_line for word in seq):
                    matched_category = category
                    break
            if matched_category:
                break

        if matched_category:
            totals[matched_category] += amount
            print(f"Match: [{matched_category}] -> {clean_line} ({amount})")
        else:
            print(f"Intet match fundet for: {clean_line}")

    bilag = [[cat, round(amt, 2)] for cat, amt in totals.items()]
    total_moms = sum(item[1] for item in bilag)
    bilag.append(['Total inkl. moms', round(total_moms, 2)])
    return bilag

def pdf_to_csv(pdfFile, output, arg):
    data = [['Kategori', 'Belød']]

    # Saml alle linjer fra ALLE sider først
    all_lines = []

    with pdfplumber.open(pdfFile) as pdf:
        for p in pdf.pages:
            text = p.extract_text()
            if text:
                lines = text.split("\n")
                all_lines.extend(lines)

    # Kør kun kategoriseringen én gang på hele PDF'en
    print(arg)
    match arg:
        case "c":
            out = check_carls(all_lines)
        case "d":
            out = check_drinx(all_lines)
        case "cl":
            out = check_carls_tilskud(all_lines)
        case "nem":
            out = nemlig_bilag(all_lines)
        case _:
            print("Type not supported.")
            return

    data += out

    frame = pd.DataFrame(data)
    frame.to_csv(output, index=False, header=False)


if len(sys.argv) < 3 or len(sys.argv) > 3:
    print("Usage: python3 RKasserG.py [bilag type] [file path]")
else:
    place = sys.argv[1]
    file = sys.argv[2]
    output = file.replace(".pdf", ".csv")
    pdf_to_csv(file, output, place)

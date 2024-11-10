import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

#################################################
# powerbeam 3K Leuchte RGB werte aus Datenblatt LED aquaristik
### Hauptlicht   R:35%  G:45% B:20%
# R: hex(int(255*35/100)) = 0x59
# G: hex(int(255*45/100)) = 0x72
# B: hex(int(255*20/100)) = 0x33
### Sunrise      R:67%  G:29% B:5%
# R: hex(int(255*67/100)) = 0xAA
# G: hex(int(255*29/100)) = 0x49
# B: hex(int(255*5 /100)) = 0x0C
### Moonlight    R:5%  G:10% B:86%
# R: hex(int(255*5 /100)) = 0x0C
# G: hex(int(255*10/100)) = 0x19
# B: hex(int(255*86/100)) = 0xDB

# Kanal- und Farbzuteilung (Original RGB-Werte)
original_channel_colors = [
    to_rgb("#597233"),  # powerBeam 3K Leuchte Hauptlicht
    to_rgb("#AA490C"),  # powerBeam 3K Leuchte Sunrise
    to_rgb("#0C19DB"),  # powerBeam 3K Leuchte Moonlight   
    to_rgb("#000000")   # CO2 Ventil Kanal
]

# Korrigierte RGB-Werte .. Farben Wirkung für Betrachter am Aquarium (subjektiv) 
corrected_channel_colors = [
    to_rgb("#FFFFFF"),  # Angepasste Farbe für Hauptlicht
    to_rgb("#FF9933"),  # Angepasste Farbe für Sunrise
    to_rgb("#944DFF"),  # Angepasste Farbe für Moonlight
    to_rgb("#000000")   # CO2 Ventil Kanal
]


# Parameter für Correction by function
correction_gamma = 2.2
correction_R     = 1.0
correction_G     = 1.0
correction_B     = 1.0


# Kanalnamen für die Beschriftung
channel_names = ["Hauptlicht", "Sunrise", "Moonlight","CO2"]
channel_color = ["orange","red","blue","black"]   # für Kanal Plot


# Switch-on Schwellenwerte für die Kanäle
thresholds = [0.10, 0.01, 0.01, 0.01]  # 10% für Hauptlicht, 1% für Sunrise und Moonlight

# Maximale Lichtstrom-Werte (in Lumen) für jeden Kanal
max_lumen = [33582, 1185, 650, 0]  # Hauptlicht, Sunrise, Moonlight

# AblaufListe   17:30 ==> 17.5
AblaufListe = {
    'PRG G (Hauptlicht)': [
        (0,   0.0),    # a new day is born
        (7,   0.0),    # Beginn Morgendämmerung
        (11,  0.8),    # maximum für den Tag erreicht
        (17,  0.8),    # bis 17:00 halten
        (19,  0.0)     # Hauptlicht wieder runter dimmen
    ],
    'PRG H (Sunrise)': [
        (0,   0.0),    # a new day is born
        (7,   0.0),    # Beginn Morgendämmerung
        (9,   1.0),    # Morgendämmerung max
        (10,  0.0),     
        (17,    0.0),    # Sonnenuntergang Lichtspiel / mehrmals
        (17.5,  1.0),    
        (18,    0.0),    
        (18.5,  1.0),    
        (19,    0.0),    
        (19.5,  1.0),    
        (20,    0.0),    
        (20.5,  1.0),    
        (21,    0.0)
    ],
    'PRG I (Moonlight)': [
        (0,   0.2),    # a new day is born
        (6,   0.2),    # Mond tritt ab
        (7,   0.8),    # noch mal hoch für Farbeffekt
        (8,   0.0),    # Tagsüber aus
        (17.5, 0.0),   # mehrmaliges Sonnuntergang / Mondspiel
        (18.0, 1.0),
        (18.5, 0.0),
        (19.0, 1.0),
        (19.5, 0.0),
        (20.0, 1.0),
        (20.5, 0.0),
        (21.0, 1.0),
        (23.0, 0.2)     # halte einen Level von 20% über Nacht
    ],
    'PRG J (CO2)': [
        (0,     0.0),    # a new day is born
        (9,     0.0),    # bis Lichthauptphase CO2 aus
        (9.01,  1.0),    # sehr kurze Rampe auf 100%
        (17,    1.0),    # halten
        (17.01, 0.0)     # kurze Rampe auf aus und bleibt aus
    ]
}

channel_program_assignments = ['PRG G (Hauptlicht)', 'PRG H (Sunrise)', 'PRG I (Moonlight)','PRG J (CO2)']

def interpolate_brightness(time, program):
    times = np.array([t[0] * 60 for t in program])
    brightness_values = np.array([t[1] for t in program])
    return np.interp(time, times, brightness_values)

def apply_gamma_correction(rgb, gamma=2.2):
    return np.power(rgb, 1 / gamma)

def apply_color_correction(rgb):
    """
    Applies color correction to reduce green/yellow and enhance red/blue.
    """
    r, g, b = rgb
    r *= correction_R  # Enhance red, adjust to prevent oversaturation
    g *= correction_G  # Reduce green
    b *= correction_B  # Enhance blue
    return np.clip([r, g, b], 0, 1) ## limited by computer screen posibilities

# Berechnung der Helligkeits- und Farbprofile
total_minutes = 24 * 60
brightness_values = np.zeros((total_minutes, len(original_channel_colors)))
resulting_colors = np.zeros((total_minutes, 3))             # true RGB Farbwert bassierend auf Angaben aus Datenblatt
table_corrected_colors = np.zeros((total_minutes, 3))       # Farbe korrigiert auf Basis der empfunden RGB Werte (zweite Tabelle)
function_corrected_colors = np.zeros((total_minutes, 3))    # Farbe korrigiert auf Basis der Korrekturfunktion

for minute in range(total_minutes):
    total_rgb = np.array([0.0, 0.0, 0.0])
    total_table_corrected_rgb = np.array([0.0, 0.0, 0.0])
    total_function_corrected_rgb = np.array([0.0, 0.0, 0.0])  # Für Gamma 1.8
    
    for ch in range(len(original_channel_colors)):
        program_name = channel_program_assignments[ch]
        brightness = interpolate_brightness(minute, AblaufListe[program_name])  # Nutzung von AblaufListe
        #brightness = round(brightness, 3)
        
        if brightness >= thresholds[ch]:
            brightness_values[minute, ch] = brightness
            # true RGB
            scaled_color = np.array(original_channel_colors[ch]) * brightness * (max_lumen[ch] / max(max_lumen))
            total_rgb += scaled_color
            # table corrected
            corrected_scaled_color = np.array(corrected_channel_colors[ch]) * brightness 
            total_table_corrected_rgb += corrected_scaled_color
            # function corrected color
            corrected_scaled_color = apply_color_correction(apply_gamma_correction(np.array(original_channel_colors[ch]) * brightness * (max_lumen[ch] / max(max_lumen)),gamma=correction_gamma))
            total_function_corrected_rgb += apply_gamma_correction(corrected_scaled_color, gamma=2.4)  # Gamma 1.8
    
    resulting_colors[minute] = np.clip(total_rgb, 0, 1)
    table_corrected_colors[minute] = np.clip(total_table_corrected_rgb, 0, 1)
    function_corrected_colors[minute] = np.clip(total_function_corrected_rgb, 0, 1)

# Zeitachsen-Labels
time_labels = [f"{int(hr)}:00" for hr in np.linspace(0, 24, 25)]

# Diagramm erstellen
fig, (ax0, ax1, ax2, ax3, ax4) = plt.subplots(5, 1, figsize=(15, 18), gridspec_kw={'height_ratios': [1, 2, 1, 1, 1]})


# Darstellung der Grundfarben sowie der korrigierten Farben und funktionalen korrigierten Farben in einer Matrix
for i, name in enumerate(channel_names[:-1]):
    # Original RGB Vorschau
    ax0.add_patch(plt.Circle((i * 3 + 0.5, 0.5), 0.1, color=original_channel_colors[i], ec='black'))
    ax0.text(i * 3 + 0.7, 0.45, f"{name} (RGB spectrum)", ha='left')
    
    # Korrigierte RGB Vorschau
    ax0.add_patch(plt.Circle((i * 3 + 0.5, 0.5 - 0.2), 0.1, color=corrected_channel_colors[i], ec='black'))
    ax0.text(i * 3 + 0.7, 0.45 - 0.2, f"{name} (Korrigiert table)", ha='left')

    # Funktional korrigierte RGB Vorschau
    functional_corrected_color = apply_color_correction(apply_gamma_correction(corrected_channel_colors[i], gamma=correction_gamma))
    ax0.add_patch(plt.Circle((i * 3 + 0.5, 0.5 - 0.4), 0.1, color=functional_corrected_color, ec='black'))
    ax0.text(i * 3 + 0.7, 0.45 - 0.4, f"{name} (Korrigiert function)", ha='left')

ax0.set_xlim(0, 9)
ax0.set_ylim(-0.5, 1)
ax0.axis('off')

# Darstellung der Helligkeit jedes Kanals über den Tag
for ch in range(len(original_channel_colors)):
    ax1.plot(np.linspace(0, 24, total_minutes), brightness_values[:, ch] * 100, label=f"Kanal {ch+1} - {channel_program_assignments[ch]}",color = channel_color[ch])
ax1.set_title("Helligkeitsprofile der Kanäle")
ax1.set_xlabel("Zeit (Stunden)")
ax1.set_ylabel("Helligkeit (%)")
ax1.set_ylim(0, 110)
ax1.set_xlim(0, 24)
ax1.set_xticks(np.linspace(0, 24, 25))
ax1.set_xticklabels(time_labels)
ax1.legend()

# Originales Farbverlaufs-Diagramm
ax2.imshow([resulting_colors], aspect='auto', extent=[0, 24, 0, 1])
ax2.set_yticks([])
ax2.set_xticks(np.linspace(0, 24, 25))
ax2.set_xticklabels(time_labels)
ax2.set_title("RGB spectrum Farbverlauf über 24 Stunden")

# Farbverlaufs-Diagramm mit korrigierten Farben 
ax3.imshow([function_corrected_colors], aspect='auto', extent=[0, 24, 0, 1])
ax3.set_yticks([])
ax3.set_xticks(np.linspace(0, 24, 25))
ax3.set_xticklabels(time_labels)
ax3.set_title("automatische Korrektur (Helligkeit & Farbe)")

# Farbverlaufs-Diagramm mit impressions Farben
ax4.imshow([table_corrected_colors], aspect='auto', extent=[0, 24, 0, 1])
ax4.set_yticks([])
ax4.set_xticks(np.linspace(0, 24, 25))
ax4.set_xticklabels(time_labels)
ax4.set_title("empfundener Farbverlauf (grau repräsentiert Weiß Helligkeitsabstufung)")



plt.subplots_adjust(hspace=0.7) 
plt.savefig("Aquarium_Beleuchtung.png")  # Speichert das Bild mit anpassbarem Rand
plt.show()


# Ausgabe aller Programme erstellen

# Dateiname
file_name = 'programs.txt'

# Öffnen oder Erstellen der Datei im Schreibmodus
with open(file_name, 'w') as file:
    # Iteriere durch alle Programme in der AblaufListe
    for program_name, program in AblaufListe.items():
        file.write(f'{program_name}:\n')
        
        # Iteriere durch die Zeit- und Helligkeitseinträge und schreibe sie ins File
        for time, brightness in program:
            time_str = f"{int(time)}:{int((time % 1) * 60):02d}"  # Zeit im Format hh:mm
            file.write(f'  {time_str} - {brightness*100:.1f}%\n')
        
        # Füge eine Leerzeile nach jedem Programm hinzu
        file.write('\n')

print(f"Die Programme wurden in die Datei '{file_name}' gespeichert.")


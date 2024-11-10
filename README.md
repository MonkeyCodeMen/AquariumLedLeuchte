Wir haben uns eine neue 3 Kanal LED Aquarium Beleuchtung zugelegt 
damit kann man wirklich die Pflanzen / Steine und natürlich auch die Fische wunderschön in Szene setzen

nach einigen versuchen zur Planung der Steuerungszeiten und einem Excel Sheet zum dartsellen der An und Aus zeiten 
habe ich für meine Frau eine Visualisierung geschrieben 

die Programme werden ähnlich wie in der Steuerung definiert
das Programm stellt nun die An und Ausschaltzeiten/Rampen da

Anhand der TRUE RGB werte kann man abschätzen wann am besten das CO2 eingeschlaten werden sollte

und hand der visuellen Impression ganz unten könnt ihr in etwa dei Wirkung in eurem Aquarium abschätzen. Jedch wirken die Farben natürlich 
in jedem Aquarium anders, dann passt einfach die korrigierten Farben an : 
corrected_channel_colors = [
    to_rgb("#FFFFFF"),  # Angepasste Farbe für Hauptlicht
    to_rgb("#FF9933"),  # Angepasste Farbe für Sunrise
    to_rgb("#944DFF"),  # Angepasste Farbe für Moonlight
    to_rgb("#000000")   # CO2 Ventil Kanal
]



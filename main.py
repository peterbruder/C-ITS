import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import re
import base64
from branca.element import Template, MacroElement
import streamlit.components.v1 as components
from pathlib import Path
import os

def show_pdf(file_path, height=600):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="{height}px" type="application/pdf" scrolling="no"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

st.set_page_config(
    page_title="C-ITS in NRW",       # 👉 Titel im Browser-Tab
    page_icon="🚦",                  # 👉 Optional: Emoji oder Pfad zu Icon
    layout="wide"                    # 👉 Optional: Seitenlayout
)

# Bild laden
with open("Abbildungen/logo-mulnv-farbig_rgb.png", "rb") as f:
    data = f.read()
    encoded = base64.b64encode(data).decode()

st.sidebar.image("Abbildungen/logo-mulnv-farbig_rgb.png", use_container_width=True)
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] img {
        border-radius: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Große Logos zentriert in voller Breite
st.sidebar.image("Abbildungen/LOGO_FH_Muenster.png", use_container_width=True)
st.sidebar.image("Abbildungen/Logo_FGV.png", use_container_width=True)
st.sidebar.image("Abbildungen/Logo_FB_ETI_2.svg", use_container_width=True)


def load_and_clean_data(csv_path):
    """Load and clean CSV data silently"""
    # Try different CSV formats
    load_attempts = [
        {'sep': ';', 'decimal': ','},
        {'sep': ';', 'decimal': '.'},
        {'sep': ',', 'decimal': '.'},
        {'sep': '\t', 'decimal': ','},
        {'sep': '\t', 'decimal': '.'},
    ]
    
    df = None
    for params in load_attempts:
        try:
            df = pd.read_csv(csv_path, **params)
            if len(df.columns) > 5 and len(df) > 0:
                break
        except:
            continue
    
    if df is None:
        return None
    
    # Clean coordinates
    def clean_coordinate(value):
        if pd.isna(value):
            return None
        coord_str = str(value).strip().replace(',', '.')
        coord_str = re.sub(r'[^0-9.-]', '', coord_str)
        try:
            return float(coord_str)
        except:
            return None
    
    # Clean coordinate columns
    for col in ['Latitude', 'Longitude']:
        if col in df.columns:
            df[col] = df[col].apply(clean_coordinate)
    
    # Remove rows without valid coordinates
    df = df.dropna(subset=['Latitude', 'Longitude'])
    
    # Clean numeric columns
    for col in ['RSU', 'OBU']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df


# Main app
st.title("Systemstudie: Zielorientierte Implementierung von kooperativen intelligenten Verkehrssystemen in Nordrhein-Westfalen")

####################################################################################################################################################
#Anwendungsfälle

st.subheader("C-ITS-Dienste nach C-Roads Germany")

# Kartenliste (Bildpfad, Rückseitentext)
cards = [
    ("Abbildungen/EVA.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Einsatzfahrzeug-Warnung</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>EVA warnt frühzeitig vor sich nähernden oder stehenden Einsatzfahrzeugen. Erhöht die Aufmerksamkeit für die Bildung von Rettungsgassen und trägt zur Verkehrssicherheit bei.</span>"""),

    ("Abbildungen/GLOSA.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Restrot-Anzeige, Grüne Welle- und Verzögerungsassistent</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>GLOSA informiert über Ampelphasen und optimale Geschwindigkeit. Erhöht Fahrkomfort, spart Energie und hilft, unnötiges Bremsen oder Beschleunigen zu vermeiden.</span>"""),

    ("Abbildungen/IVS.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Verkehrszeichendarstellung im Fahrzeug</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>IVS zeigt Verkehrszeichen im Fahrzeug an – auch dynamische. Der Fahrer wird kontinuierlich über aktuelle Regelungen informiert, was Sicherheit und Aufmerksamkeit verbessert.</span>"""),

    ("Abbildungen/MVW.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Warnung vor Einsatzfahrzeugen des Straßenbetriebsdienstes</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>MVW warnt vor langsamen oder stehenden Fahrzeugen wie Mäh- oder Winterdienstfahrzeugen – insbesondere bei eingeschränkter Sicht. Erhöht die Sicherheit und verringert Unfallrisiken.</span>"""),

    ("Abbildungen/PVD.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Nutzung von Fahrzeugdaten für die Verbesserung der Verkehrslageerkennung</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>Statusmeldungen (PVD) von Fahrzeugen ermöglichen eine präzisere Verkehrslageanalyse – besonders dort, wo stationäre Sensorik fehlt. Grundlage für dynamisches Verkehrsmanagement.</span>"""),

    ("Abbildungen/RouteAdvice.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Vernetzte & Kooperative Navigation</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>Unterstützt die stadt- und regionsübergreifende Routenlenkung durch vernetzte Verkehrsstrategien. Ziel ist eine abgestimmte Navigation via G5 und App – etwa an urbanen Knotenpunkten.</span>"""),

    ("Abbildungen/RWW.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Baustellenwarnung</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>Warnt frühzeitig vor Baustellen auf Autobahnen, um Unfälle und Staus zu vermeiden. Die Infos werden per G5 oder DAB direkt ins Fahrzeug übertragen.</span>"""),

    ("Abbildungen/SWD.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Verminderung von Stauausbreitung im Autobahnnetz</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>Shockwave Damping harmonisiert den Verkehrsfluss durch Geschwindigkeitsempfehlungen im Fahrzeug. Ziel ist es, Stauwellen zu verhindern oder deren Ausbreitung zu mindern.</span>"""),

    ("Abbildungen/TJW.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Stauendewarnung</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>Warnt frühzeitig vor einem abrupten Stauende – etwa hinter Kurven oder Kuppen – um Auffahrunfälle zu vermeiden und Fahrerreaktionen rechtzeitig auszulösen.</span>"""),

    ("Abbildungen/TSP.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Prioritätsanforderungen für Ampelanlagen (TSP)</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>TSP ermöglicht eine bevorzugte Ampelschaltung für Einsatz- und ÖPNV-Fahrzeuge. Verkürzt Reaktionszeiten, verbessert Pünktlichkeit und erhöht die Verkehrssicherheit.</span>"""),

    ("Abbildungen/VRU.png", 
    """<strong style='font-size:18px; font-family:sans-serif;'>Schutz schwacher Verkehrsteilnehmer</strong><br>
    <span style='font-size:13px; font-family:sans-serif;'>Warnt vor gefährdeten Verkehrsteilnehmenden wie Radfahrenden – besonders bei schlechter Sicht oder an Kreuzungen. Erhöht Sicherheit durch vorausschauende Fahrzeugwarnung.</span>""")
]

# Hilfsfunktion zur base64-Kodierung
def image_to_base64(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# HTML mit CSS-Styles
html = """
<div style="display:flex; justify-content:center;">
  <div style="max-width:1000px;">
<style>
.grid-container {
    display: grid;
    grid-template-columns: repeat(4, 300px);
    gap: 20px;
    justify-content: center;
    padding: 20px;
}
.flip-box {
    background-color: transparent;
    width: 300px;
    height: 300px;
    perspective: 1000px;
}
.flip-box-inner {
    position: relative;
    width: 100%;
    height: 100%;
    text-align: center;
    transition: transform 0.6s;
    transform-style: preserve-3d;
}
.flip-box:hover .flip-box-inner {
    transform: rotateY(180deg);
}
.flip-box-front, .flip-box-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 18px;
    color: white;
    padding: 5px;
    box-sizing: border-box;
}
.flip-box-front {
    background-color: transparent;
    flex-direction: column;
}
.flip-box-front img {
    max-width: 100%;
    max-height: 100%;
    object-fit: cover;
    border-radius: 10px;
}
.flip-box-back {
    background-color: #0014A0;
    transform: rotateY(180deg);
    padding: 15px;
    text-align: center;
    display: flex;             /* ← hinzufügen */
    flex-direction: column;    /* ← hinzufügen */
    justify-content: center;   /* optional: mittig */
    align-items: center;       /* optional: mittig */
}

<div style="text-align:center; font-size:12px; font-family:sans-serif; color:#666; margin-top:30px; line-height:1.5;">
    (C) C-Roads Germany / <a href='https://www.c-roads-germany.de' target='_blank' style='color:#888;'>www.c-roads-germany.de</a><br>
    C-Roads Germany (o. J.): <em>C-ITS-Dienste</em>. Online verfügbar unter: 
    <a href='https://www.c-roads-germany.de' target='_blank' style='color:#888;'>https://www.c-roads-germany.de</a>
    (Zugriff am: 12.07.2025).

</div>
</style>
<div class="grid-container">
"""


# Karten im HTML erzeugen
for image_path, back_text in cards:
    img_base64 = image_to_base64(image_path)
    if img_base64:
        html += f"""
        <div class="flip-box">
            <div class="flip-box-inner">
                <div class="flip-box-front">
                    <img src="data:image/png;base64,{img_base64}" alt="">
                </div>
                <div class="flip-box-back">{back_text}</div>
            </div>
        </div>
        """

html += "</div>"

# Anzeige in Streamlit
components.html(html, width=2800, height=1000, scrolling=False)

st.info("""© C-Roads Germany / [www.c-roads-germany.de](https://www.c-roads-germany.de)
C-Roads Germany (o. J.): *C-ITS-Dienste*. Online verfügbar unter: [https://www.c-roads-germany.de](https://www.c-roads-germany.de) (Zugriff am: 11.07.2025)""")

####################################################################################################################################################
# Karte 

# Load data
csv_path = "Dokumente/C-ITS_Projekte_Deutschland.csv"
df = load_and_clean_data(csv_path)

if df is None or len(df) == 0:
    st.error("Daten konnten nicht geladen werden.")
    st.stop()

st.expander("Status quo von C-ITS in Deutschland")
# Create map
st.subheader("C-ITS Projekte im DACH-Raum")

center_lat = df["Latitude"].mean()
center_lon = df["Longitude"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles="CartoDB positron")

legend_html = """
{% macro html() %}
<div style="
    position: fixed; 
    bottom: 50px;
    left: 50px;
    width: 180px;
    background-color: white;
    border: 1px solid lightgray;
    border-radius: 5px;
    padding: 10px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
    font-size: 14px;
    z-index:9999;
">
    <b> Legende</b><br>
    <i class="fa fa-map-marker fa-1x" style="color:green"></i> Laufend<br>
    <i class="fa fa-map-marker fa-1x" style="color:blue"></i> Abgeschlossen<br>
    <i class="fa fa-map-marker fa-1x" style="color:gray"></i> Unbekannt
</div>
{% endmacro %}
"""

legend = MacroElement()
legend._template = Template(legend_html)
m.get_root().add_child(legend)

# Farbdefinition nach Status
def get_marker_color(status):
    if str(status).strip().lower() == "laufend":
        return "green"
    elif str(status).strip().lower() == "abgeschlossen":
        return "blue"
    else:
        return "gray"

# Add markers

# Marker setzen
for _, row in df.iterrows():
    # Farbliche Darstellung basierend auf "Status"
    marker_color = get_marker_color(row.get("Status", ""))

    # Erste Spalte: Projektdetails
    left_column = f"""
        <div style="width: 48%; float: left; padding-right: 2%;">
            <h4 style="color: #1f77b4; margin-top:0;">{row['Projekt']}</h4>
            <p><strong>Ort:</strong> {row['Ort']}</p>
    """
    for col in ['Jahr', 'Kommunikationstechnologie', 'TSP via C-ITS', 'GLOSA',
                'weitere C-ITS-Services', 'Systemarchitektur', 'Ausbaustufe']:
        if col in df.columns:
            left_column += f"<p><strong>{col}:</strong> {row[col]}</p>"
    left_column += "</div>"

    # Zweite Spalte: Beschreibung (falls vorhanden)
# Zweite Spalte: Beschreibung + Projektlink
    right_column = ""
    if 'Beschreibung' in df.columns:
        right_column = f"""
            <div style="width: 48%; float: right;">
                <h4 style="color: #1f77b4;">Beschreibung</h4>
                <p style="text-align: justify;">{row['Beschreibung']}</p>
        """

        # Projektlink hinzufügen (wenn vorhanden)
        if 'Projektlink' in df.columns and pd.notna(row['Projektlink']) and row['Projektlink'].strip() != "":
            right_column += f"""
                <p><a href="{row['Projektlink']}" target="_blank" style="color:#007BFF; text-decoration: none;">
                    🔗 Weiterführende Informationen
                </a></p>
            """

        right_column += "</div>"

    # Kombiniertes HTML für Popup
    popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 500px; overflow: hidden;">
            {left_column}
            {right_column}
        </div>
    """

    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=folium.Popup(popup_html, max_width=550),
        tooltip=f"{row['Projekt']} - {row['Ort']}",
        icon=folium.Icon(color=marker_color, icon="info-sign")
    ).add_to(m)


# Display map
folium_static(m, width=2800, height=600)

st.info("""
Daten entnommen aus Forschungsgesellschaft für Straßen- und Verkehrswesen (FGSV) (2024): Hinweise für den Technologiewechsel C-ITS an Lichtsignalanlagen (H TwLSA). Eigene Darstellung.""")

####################################################################################################################################################
# AP 1: Lessons learned 
st.subheader("Lessons learned aus den Pilotprojekten")
st.text(" Die folgende Ausarbeitung fasst die in verschiedenen nationalen Studien und praxisnahen Projekte gewonnenen Erkenntnisse in sechs Unterpunkte zusammen. Diese dienen dazu, die Ergebnisse übersichtlich zu präsentieren und einen Vergleich zwischen den jeweiligen Ansätzen und Ergebnissen zu ermöglichen.")
# Layout mit zwei Spalten
col1, col2 = st.columns([1, 2])

# Linke Seite: Auswahlboxen
with col1:
    auswahl = st.radio(
        "Wählen Sie einen Themenbereich:",
        [
            "Interoperabilität",
            "Technische Voraussetzungen und Verfahren",
            "Datensicherheit & Schutz",
            "Akteure",
            "Migrationspfade an LSA",
            "Investitions- und Betriebskosten"
        ]
    )

# Rechte Seite: Beschreibungstexte
with col2:
    if auswahl == "Interoperabilität":
        st.markdown("""
Der europaweite C-Roads-Ansatz hat hinsichtlich der **Interoperatbilität** wichtige Grundlagen geschaffen, etwa durch standardisierte Protokolle wie SREM/SSEM, SPATEM, MAPEM, welche eine übergreifende Kommunikation zwischen dem Fahrzeug und der Infrastruktur (V2I) ermöglicht. Allerdings zeigt sich auch, dass offene Schnittstellen wie OCIT-O/C zwar verfügbar sind, sie müssen aber weiterentwickelt und verbindlich normiert werden, um dauerhaft zuverlässig zu funktionieren. Ohne klare Standards bleibt Interoperabilität oft theoretisch. \n
In verschiedenen Testumgebungen hat sich in den Projekten gezeigt, dass die beiden Sendetechnologien ITS-G5 und C-V2X (LTE-V2X) nicht miteinander kompatibel sind, sofern sie im gleichen Frequenzbereich betrieben werden (TEMPUS). Es besteht daher Klärungsbedarf, wie beide Kommunikationsstandards künftig koexistieren können oder ob sich langfristig eine der Technologien durchsetzen wird. Die im Rahmen von TEMPUS gewonnenen Erkenntnisse unterstützen andere Kommunen bei der Einführung vergleichbarer Systeme und verringern deren Aufwand für Anpassung und Integration. [1] (S. 29) \n
Ein offener Zugang für Start-ups, Forschung und Industrie steigert die Innovationskraft und fördert die Akzeptanz neuer Systeme. Damit keine Insellösungen entstehen, ist eine frühzeitige Standardisierung, reale Erprobung und ein offener Austausch zwischen allen Beteiligten notwendig. \n
•	C-Roads schafft mit standardisierten Protokollen übergreifende Kommunikation.\n
•	OCIT-O/C-Schnittstellen müssen verbindlich normiert und weiterentwickelt werden.\n
•	TEMPUS zeigt, dass ITS-G5 und C-V2X auf dem gleichen Frequenzbereich nicht kompatibel sind  \n
•	Offener Zugang und frühe Standardisierung fördern Innovation und verhindern Insellösungen.
        """)
    elif auswahl == "Technische Voraussetzungen und Verfahren":
        st.markdown("""
        Die Betrachtung abgeschlossener und aktueller C-ITS-Projekte zeigt, dass für einen reibungslosen Einsatz von C-ITS an LSA einige **technische Voraussetzungen und Verfahren**  notwendig sind, wie z.~B. flächendeckende, interoperable Kommunikation, standardisierte Schnittstellen, die Integration von TSP- (Traffic Signal Priority) und GLOSA-Services (Green Light Optimal Speed Advisory), sowie die enge Verknüpfung mit der Infrastruktur auf Basis einer modularen Systemarchitektur.\n
**Kommunikation**\n
Die Grundlage für eine einheitliche, interoperable Kommunikationsinfrastruktur zwischen Fahrzeug und Infrastruktur sind standardisierte Nachrichtentypen wie MAPEM, SPATEM, SREM, SSEM, CAM und CPM. Diese Kommunikation erfolgt meist auf Basis von ITS-G5 (WLANp) oder C-V2X. Dies konnte mithilfe des Projektes BiDiMoVe aus Hamburg erfolgreich erprobt werden. Es war gelungen eine Busbevorrechtigung an der LSA mithilfe von C-ITS und ITS-G5-Funkstandards umzusetzen.\n
**Offene Schnittstellen**\n                 
Der Austausch von Informationen zwischen Lichtsignalanlage (LSA) und der Zentrale erfolgt über die OCIT-O Schnittstelle, während der Datenaustausch zwischen den Zentralen über OCIT-C realisiert wird. Dieser Ansatz wurde bereits im Projekt BiDiMoVe erfolgreich angewendet. \n
**ETA-Berechnung**\n
ETA-Berechnung (Estimated Time of Arrival) wurden in den Projekte ABSOLUT I und HERCULES erprobt. In dieser Studie hat sich gezeigt, dass eine fahrzeugseitige ETA-Ermittlung den Vorteil bietet, individuelle Fahreigenschaften besser berücksichtigen zu können und dadurch die Prognosequalität gute Werte erzielte, während eine zentrale Berechnung externe Einflüsse wie z.B. das Wetter oder die Verkehrslage genauer in die Prognose einfließen lassen kann.\n
**Synchronisation von TSP und GLOSA**\n                    
Viele Projekte zur Verbesserung des Verkehrsflusses an Lichtsignalanlagen belegen, dass die Kombination von TSP- (Traffic Signal Priority) und GLOSA-Services (Green Light Optimal Speed Advisory) entscheidend für eine verbesserte Verkehrssteuerung ist. Allerdings sind die unterschiedlichen Zielsetzungen zwischen Echtzeitprognosen und Priorisierungsanforderungen schwierig in Einklang zu bringen (ACCorD; SIRENE).\n                    
**Sensordichte**\n
Eine erhöhte Sensordichte und die Verknüpfung mit der Infrastruktur (z.~B. LiDAR, Wärmebildkameras) verbessert die Erfassung des Verkehrsgeschehens und ist insbesondere bei autonomen Fahrzeugen oder zum Schutz vulnerabler Verkehrsteilnehmender (VRU) essenziell (HEAT; FLASH; TEMPUS).\n
**Systemarchitektur**\n
In den Projekten zeigte sich, dass die Systemarchitektur offen und modular sein muss, um den unterschiedlichen Anforderungen von Verkehrsarten, Fahrzeugtypen und Betreiberstrukturen gerecht zu werden. Die Integration von Shuttles, Lkw, ÖPNV und Radverkehr in ein gemeinsames System stellt hohe Anforderungen an die Architekturflexibilität (ITS-Cube; VERONIKA). Ebenso zeigte sich, dass eine hohe Systemkomplexität ein durchdachtes Datenmanagement sowie Monitoring- und Leitstellenkonzepte erfordert (HEAT; LOGIN).\n                                                                           
•	Eine genormte interoperable Kommunikation ist Grundvoraussetzungen für eine übergreifende Nutzung (BiDiMoVe, HEAT).\n
•	Präzise ETA und standardisierte Schnittstellen (ABSOLUT I, BiDiMoVe).\n
•	Kombination von TSP/GLOSA und hohe Sensordichte verbessern Verkehr und Sicherheit (ACCorD, HEAT).\n
•	Offene, modulare Architektur und gutes Datenmanagement (ITS-Cube, VERONIKA).""")
    elif auswahl == "Datensicherheit & Schutz":
        st.markdown("""
        Im Bereich **Datenschutz und -sicherheit** hat sich gezeigt, dass PKI-Systeme (Public Key Infrastructure) eine Voraussetzung für eine sichere Kommunikation im C-ITS-Umfeld sind. Sie ermöglichen eine zuverlässige, geschützte Authentifizierung zwischen Fahrzeugen und Infrastruktur.\n  
Die Projekte HEAT, BiDiMoVe und MINGA haben sich mit der Implementierung von PKI-Systemen auseinandergesetzt und haben demonstriert, dass der Einsatz  technisch umsetzbar ist. Die größte Herausforderung besteht im dauerhaften Betrieb. In den genannten Projekten kamen deshalb Pilot-PKI-Lösungen zum Einsatz, da eine verbindliche nationale oder europäische Lösung zum Zeitpunkt der Umsetzung noch nicht vorlag (HEAT, BiDiMoVe, MINGA).\n
Neben den ITS-Diensten können auch personenbezogene Daten betroffen sein, wie zum Beispiel Fahrzeugkennungen oder Fahrprofile zu datenschutzrechtlichen Bedenken im Zusammenhang mit app-basierter Kommunikation führen. Daher sind klare Regelungen zur Datenverarbeitung, -speicherung und -nutzung erforderlich, um rechtliche Vorgaben und die gesellschaftliche Akzeptanz zu gewährleisten. Darüber hinaus sind rechtliche Rahmenbedingungen  notwendig, um den Datenschutz in vernetzten Mobilitätssystemen dauerhaft sicherzustellen.\n
•	PKI-Systeme sind zentral für sichere Kommunikation in C-ITS (HEAT, BiDiMoVe, MINGA).\n
•	Der dauerhafte Betrieb und die Interoperabilität von PKI-Lösungen bleiben herausfordernd (HEAT, BiDiMoVe, MINGA).\n
•	Datenschutz bei app-basierter Kommunikation und individuellen Fahrprofilen (BiDiMoVe, HEAT). (?)\n
•	Neben technischer Sicherheit sind klare rechtliche Regelungen zur Datenverarbeitung essenziell.\n
        """)
    elif auswahl == "Akteure":
        st.markdown("""
Die C-ITS-Projekte zeigen, dass der Erfolg maßgeblich von der frühzeitigen Einbindung und engen Zusammenarbeit aller **Akteure** abhängt, davon sind insbesondere Kommunen, Verkehrsunternehmen, Infrastrukturbetreibern und Technologieanbietern betroffen (BiDiMoVe, LOGIN). Zudem ist eine klare Abstimmung zwischen Fahrzeug- und Infrastrukturseite essenziell, um Kommunikationsprozesse reibungslos umzusetzen (HEAT, SIRENE).
Verkehrsunternehmen leisten einen wichtigen Beitrag zur Bewertung der praktischen Wirkung von Priorisierungen und Fahrstrategien, insbesondere im Linienbetrieb (MINGA, MENDEL). Gleichzeitig wurde deutlich, dass interdisziplinäres Projektmanagement nötig ist, um Technik, Planung und Betrieb erfolgreich zu verknüpfen (VERONIKA, ACCorD).
C-ITS funktioniert nur mit klar definierten Rollen, enger Abstimmung und einem gemeinsamen Verständnis der Systemziele.\n
•	Frühzeitige Einbindung und Zusammenarbeit aller Akteure ist entscheidend (BiDiMoVe, LOGIN).\n
•	Klare Abstimmung zwischen Fahrzeug- und Infrastrukturseite ist essenziell (HEAT, SIRENE).\n
•	Verkehrsunternehmen bewerten die Wirkung von Priorisierungen im Linienbetrieb (MINGA, MENDEL).\n
•	Interdisziplinäres Projektmanagement verbindet Technik, Planung und Betrieb (VERONIKA, ACCorD).
        """)
    elif auswahl == "Migrationspfade an LSA":
        st.markdown("""
Erfolgreiche **Migrationspfade zur Einführung von C-ITS an Lichtsignalanlagen** basieren auf einer schrittweisen, modularen Vorgehensweise. Zunächst werden bestehende Systeme durch gezielte Nachrüstungen erweitert, um erste C-ITS-Funktionen wie SPAT/MAP oder Bevorrechtigung zu ermöglichen (Kassel, München, Speyer).\n 
Die Migration erfolgt idealerweise schrittweise: Zuerst werden Pilotanlagen umgesetzt, um Erfahrungen zu sammeln und technische sowie organisatorische Herausforderungen zu identifizieren. Danach wird das System abschnittweise auf weitere Knotenpunkte und Verkehrsbereiche ausgeweitet (Hannover, München). Eine frühzeitige Planung der Zielarchitektur und die Berücksichtigung zukünftiger Standards und Kommunikationswege sind entscheidend für einen nachhaltigen Migrationspfad (Kassel, Frankfurt am Main). Zentrale Backend-Lösungen und standardisierte Protokolle verbessern die Skalierbarkeit und Wartungsintensität der Systeme (München, Speyer).\n
Der Parallelbetrieb hat sich als besonders erfolgreich herausgestellt und erleichtert die Umstellung (MINGA). Aufgrund der fehlenden bundeseinheitlichen Regelungen wurden zunächst temporäre Pilotlösungen wie Test-PKI-Systeme eingesetzt, um den sicheren Betrieb von C-ITS-Komponenten zu ermöglichen (HEAT, BiDiMoVe). Der Anschluss an bestehende Steuergeräte über standardisierte Schnittstellen wie OCIT-C oder OCIT-O ist eine grundlegende Voraussetzung für eine Integration. So können neues C-ITS-Komponenten ohne vollständigen Austausch der Infrastruktur eingebunden werden (BiDiMoVe, VERONIKA).\n
•	Schrittweise Nachrüstung bestehender Systeme ermöglicht erste C-ITS-Funktionen (Kassel, München, Speyer).\n
•	Enge Zusammenarbeit aller Akteure ist wichtig für Interoperabilität und Schnittstellenmanagement (Frankfurt am Main, Rüsselsheim).\n
•	Pilotbetrieb, Etappenmigration und frühzeitige Planung der Zielarchitektur sichern nachhaltigen Migrationspfad (Hannover, München, Kassel).\n
•	Parallelbetrieb alter und neuer Technologien sowie offene Schnittstellen erleichtern die Integration (MINGA, BiDiMoVe, VERONIKA

        """)
    elif auswahl == "Investitions- und Betriebskosten":
        st.markdown("""
        Der **Investitionsaufwand** hängt von der vorhandenen technischen Infrastruktur ab. In Städten mit bereits modernisierten Lichtsignalanlagen der standardisierten Schnittstellen konnte C-ITS vergleichsweise effizient integriert werden, da vorhandene Steuergeräte weiterverwendet oder nur geringfügig angepasst werden mussten (z.~B. BiDiMoVe, VERONIKA). Das Nachrüstung von älteren Anlagen, oftmals zusätzliche Technik oder Schnittstellenanpassungen, kann zu einem höheren Aufwand führen.\n
Für den Aufbau und sicheren Betrieb von PKI-Systemen, wie in HEAT und BiDiMoVe, werden zusätzliche technische und organisatorische Ressourcen benötigt, insbesondere für Zertifikatsmanagement, Systempflege und Support. Auch Leitstellenanbindungen und Backend-Systeme verursachen Betriebskosten, etwa für Wartung und Systemupdates (MINGA, MENDEL).\n
Mehrere Projekte machten deutlich, dass die Nutzung offener, standardisierter Schnittstellen von OCIT-C /OCIT-O und modularer Systemarchitekturen dazu beitragen kann, langfristige Betriebskosten zu senken und spätere Erweiterungen zu erleichtern (BiDiMoVe, VERONIKA, LOGIN). Frühzeitige Tests im Rahmen von Pilotbetrieben halfen zudem, technische Hürden zu identifizieren (HEAT, MINGA, MENDEL). Die Ermittlung der Kosten für die Implementierung gestaltet sich als anspruchsvoll.\n 
•	Investitionskosten hängen stark vom Modernisierungsgrad und vorhandenen Schnittstellen der LSA ab (BiDiMoVe, VERONIKA).\n
•	Nachrüstung älterer Anlagen und Aufbau sicherer PKI-Systeme erfordern zusätzliche Ressourcen (HEAT, BiDiMoVe).\n
•	Offene, standardisierte Schnittstellen und modulare Architekturen senken langfristige Betriebskosten (BiDiMoVe, VERONIKA, LOGIN).\n
•	Die Ermittlung der Kosten für die Implementierung gestaltet sich als anspruchsvoll.

        """)

####################################################################################################################################################
# AP 1: Herausforderungen
st.subheader("Herausforderungen von C-ITS in Nordrhein-Westfalen")
st.markdown(
    """
    <div style="text-align: center;">
        <img src="Abbildungen/C_ITS_AP1_Herausforderungen.png" width="800">
    </div>
    """,
    unsafe_allow_html=True
)
st.image("Abbildungen/C_ITS_AP1_Herausforderungen.png", width=900)

st.info("Eigene Darstellung (Drashe Bytyqi, 11.07.2025)")


####################################################################################################################################################
# AP 2: Projektakteure

st.subheader("Übersicht der Akteure und Ihrer Rollen für die erfolgreiche Implementierung von C-ITS")

st.image("Abbildungen/C_ITS_AP3_Projektaktuere.png", width=900)
st.info("Eigene Darstellung (Peter Bruder, 09.07.2025)")

####################################################################################################################################################
#Impressum

st.markdown("""
<hr style="margin-top: 4em;">

<div style="background-color: #f0f0f0; padding: 14px; border-radius: 6px; font-size: 0.85em; color: #333; line-height: 1.5;">
  <p><strong>Projekt:</strong> Systemstudie: Zielorientierte Implementierung von kooperativen intelligenten Verkehrssystemen in Nordrhein-Westfalen</p>
  <p><strong>Förderung:</strong> Ministerium für Umwelt, Landwirtschaft, Natur- und Verbraucherschutz des Landes Nordrhein-Westfalen (MULNV NRW)</p>
  <p><strong>Bearbeitung:</strong> FH Münster, Fachbereich Bauingenieurwesen & Fachbereich Elektrotechnik und Informatik</p>
  <p><strong>Entwicklung:</strong> Peter Bruder, M. Sc. & Drashe Bytyqi, B. Eng.</p>
  <p><strong>Laufzeit:</strong> 01. Mai 2025 – 30. April 2025</p>
  <p><strong>Version:</strong> Entwurfsfassung (Stand: Juli 2025)</p>

  <p>Diese Anwendung befindet sich derzeit in der Entwicklung. Alle Angaben erfolgen ohne Gewähr. Änderungen und Ergänzungen vorbehalten.</p>

  <p>Bei Rückfragen wenden Sie sich bitte an: 
  <a href="mailto:peter.bruder@fh-muenster.de">peter.bruder@fh-muenster.de</a></p>
</div>
""", unsafe_allow_html=True)

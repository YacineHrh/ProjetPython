import json
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

print("==================================================")
print("   INVESTIGATION SOC — INCIDENT NORDIS (2026)")
print("==================================================\n")

# --- CHARGEMENT DES DONNÉES ---
df_inv = pd.read_csv('./donnees/inventaire_parc.csv')
df_vpn = pd.read_csv('./donnees/vpn_auth.csv', parse_dates=['horodatage'])
df_mail = pd.read_csv('./donnees/mail_gateway.csv', parse_dates=['horodatage'])
df_proxy = pd.read_csv('./donnees/proxy_web.csv', parse_dates=['horodatage'])
df_fw = pd.read_csv('./donnees/firewall.csv', parse_dates=['horodatage'])

events_ad = []
with open('./donnees/ad_events.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        events_ad.append(json.loads(line))
df_ad = pd.DataFrame(events_ad)
df_ad['horodatage'] = pd.to_datetime(df_ad['horodatage'])

with open('./donnees/edr_alerts.json', 'r', encoding='utf-8') as f:
    df_edr = pd.DataFrame(json.load(f))
df_edr['horodatage'] = pd.to_datetime(df_edr['horodatage'])


# --- NIVEAU 1 : PÉRIMÈTRE & VOLUMÉTRIE ---
print("--- NIVEAU 1 : INVENTAIRE ET LOGS ---")
postes = len(df_inv[df_inv['type'] == 'poste'])
serveurs = len(df_inv[df_inv['type'] == 'serveur'])
print(f"Parc informatique : {postes} postes de travail et {serveurs} serveurs (Total: {len(df_inv)})")
print(f"Période couverte   : du {df_vpn['horodatage'].min()} au {df_vpn['horodatage'].max()}\n")


# --- NIVEAU 2 : VECTEUR D'ENTRÉE ---
print("--- NIVEAU 2 : POINT D'ENTRÉE & PHISHING ---")
phishing = df_mail[df_mail['sujet'].str.contains('Facture impayée', case=False, na=False)].iloc[0]
print(f"Mail malveillant  : Reçu par '{phishing['destinataire']}' depuis '{phishing['expediteur']}'")
print(f"Lien piégé        : {phishing['lien']}")

vpn_suspect = df_vpn[df_vpn['pays'] != 'FR']
premier_vpn = vpn_suspect[vpn_suspect['resultat'] == 'succes'].iloc[0]
print(f"Accès VPN malveillant : Compte '{premier_vpn['login']}' depuis l'IP {premier_vpn['ip_source']} ({premier_vpn['pays']}) le {premier_vpn['horodatage']}\n")


# --- NIVEAU 3 : PERSISTANCE ACTIVE DIRECTORY ---
print("--- NIVEAU 3 : ÉLÉVATION ET PERSISTANCE AD ---")
backdoor = df_ad[df_ad['compte_cree'] == 'svc_monitoring'].iloc[0]
print(f"Faux compte créé : '{backdoor['compte_cree']}' par '{backdoor['utilisateur']}' le {backdoor['horodatage']} (IP: {backdoor['ip_source']})")

elevation = df_ad[df_ad['compte_ajoute'] == 'svc_monitoring'].iloc[0]
print(f"Privilèges       : Ajouté au groupe '{elevation['groupe']}' le {elevation['horodatage']}\n")


# --- NIVEAU 4 : EXFILTRATION & IMPACT RANSOMWARE ---
print("--- NIVEAU 4 : IMPACT & EDR ---")
df_proxy['mo_envoyes'] = df_proxy['octets_envoyes'] / (1024 * 1024)
exfil_total = df_proxy[df_proxy['login'] == 'l.perrin']['mo_envoyes'].sum()
print(f"Données exfiltrées par l.perrin : {exfil_total:.2f} Mo vers 'cloud-depot-securise.example'")

alertes_critiques = df_edr[df_edr['gravite'] == 'critique']
print(f"Alertes EDR critiques non traitées : {len(alertes_critiques)} alertes ouvertes\n")


# --- GÉNÉRATION DU RAPPORT PDF ---
print("--> Génération du rapport PDF...")
doc = SimpleDocTemplate("Rapport_SOC_Investigation.pdf", pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
styles = getSampleStyleSheet()

title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1A252C'), spaceAfter=10)
h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, leading=15, textColor=colors.HexColor('#2C3E50'), spaceBefore=8, spaceAfter=4)
body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#222222'), spaceAfter=5)
cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#222222'))
cell_header = ParagraphStyle('CellHeader', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.whitesmoke, fontName='Helvetica-Bold')

# Lien de ton dépôt GitHub
LIEN_GITHUB = "https://github.com/YacineHrh/ProjetPython"

story = [
    Paragraph("Rapport d'Investigation SOC — Incident Nordis", title_style),
    Paragraph(f"<b>Code source & Dépôt GitHub :</b> <a href='{LIEN_GITHUB}' color='blue'><u>{LIEN_GITHUB}</u></a>", body_style),
    Spacer(1, 8),
    Paragraph("1. Synthèse Exécutive", h2_style),
    Paragraph("Entre le 11 et le 20 septembre 2026, l'entreprise a subi une cyberattaque majeure menant à la compromission du réseau, "
              "à l'exfiltration de <b>~853 Mo</b> de données comptables et au chiffrement des partages réseau (<code>SRV-FILE01</code>) par un rançongiciel. "
              "L'attaque a débuté par un hameçonnage (phishing), suivi d'un accès VPN illégitime, d'une élévation de privilèges (Admin du domaine) et de la suppression des sauvegardes.", body_style),
    Paragraph("2. Périmètre & Volumétrie", h2_style),
    Paragraph(f"• <b>Période d'analyse :</b> 31 août 2026 au 20 septembre 2026<br/>"
              f"• <b>Infrastructures :</b> {postes} postes de travail, {serveurs} serveurs sur 3 sites (Siège, Lyon, Lille)<br/>"
              "• <b>Sources analysées :</b> VPN, Mail, Proxy web, Active Directory, Pare-feu, EDR", body_style),
    Paragraph("3. Chronologie de l'Attaque", h2_style),
    Paragraph("<b>11/09 10:48 — Phishing :</b> Réception d'un mail piégé par <code>l.perrin</code> (poste <code>PC-SIE-1000</code>) depuis <code>comptabilite@fourniseur-x.example</code>.<br/>"
              "<b>11/09 23:17 — Accès VPN :</b> Connexion VPN réussie depuis l'IP <code>203.0.113.87</code> (Nigeria) avec le compte compromis.<br/>"
              "<b>14/09 02:29 — Persistance AD :</b> Création du compte <code>svc_monitoring</code> et ajout au groupe <b>Admins du domaine</b>.<br/>"
              "<b>19/09 03:43 — Exfiltration :</b> Transfert de 852,98 Mo vers <code>cloud-depot-securise.example</code> via le proxy.<br/>"
              "<b>20/09 03:59 - 05:25 — Ransomware :</b> Arrêt des sauvegardes puis chiffrement massif de <code>SRV-FILE01</code>.", body_style),
    Paragraph("4. Alertes EDR Ignorées", h2_style)
]

data = [
    [Paragraph("Horodatage", cell_header), Paragraph("Machine", cell_header), Paragraph("Alerte", cell_header), Paragraph("Gravité", cell_header), Paragraph("Statut", cell_header)],
    [Paragraph("11/09 11:20", cell_style), Paragraph("PC-SIE-1000", cell_style), Paragraph("Page d'hameçonnage visitée", cell_style), Paragraph("Moyenne", cell_style), Paragraph("ouvert", cell_style)],
    [Paragraph("14/09 02:57", cell_style), Paragraph("SRV-FILE01", cell_style), Paragraph("Création compte privilèges hors procédure", cell_style), Paragraph("Critique", cell_style), Paragraph("ouvert", cell_style)],
    [Paragraph("19/09 04:14", cell_style), Paragraph("PC-SIE-1000", cell_style), Paragraph("Exfiltration de données (~853 Mo)", cell_style), Paragraph("Critique", cell_style), Paragraph("ouvert", cell_style)],
    [Paragraph("20/09 03:59", cell_style), Paragraph("SRV-FILE01", cell_style), Paragraph("Suppression des sauvegardes", cell_style), Paragraph("Critique", cell_style), Paragraph("ouvert", cell_style)],
    [Paragraph("20/09 05:25", cell_style), Paragraph("SRV-FILE01", cell_style), Paragraph("Chiffrement rançongiciel", cell_style), Paragraph("Critique", cell_style), Paragraph("ouvert", cell_style)],
]

t = Table(data, colWidths=[65, 65, 190, 50, 45])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
]))
story.append(t)
story.append(Spacer(1, 6))

story.append(Paragraph("5. Recommandations Prioritaires", h2_style))
story.append(Paragraph("1. <b>Confinement :</b> Isoler <code>SRV-FILE01</code> et <code>PC-SIE-1000</code>, bloquer l'IP <code>203.0.113.87</code>.<br/>"
                       "2. <b>Assainissement AD :</b> Supprimer <code>svc_monitoring</code>, réinitialiser les mots de passe de <code>l.perrin</code>, <code>n.vincent</code> et des admins.<br/>"
                       "3. <b>SOC / EDR :</b> Activer le blocage automatique pour les alertes EDR Critiques et imposer le MFA sur le VPN.", body_style))

doc.build(story)
print("SUCCESS : Rapport PDF généré avec succès !")
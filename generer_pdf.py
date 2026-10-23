from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

doc = SimpleDocTemplate(
    "Rapport_SOC_Investigation.pdf",
    pagesize=A4,
    rightMargin=30,
    leftMargin=30,
    topMargin=30,
    bottomMargin=30
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1A252C'), spaceAfter=10
)
h2_style = ParagraphStyle(
    'H2Style', parent=styles['Heading2'], fontSize=12, leading=15, textColor=colors.HexColor('#2C3E50'), spaceBefore=8, spaceAfter=4
)
body_style = ParagraphStyle(
    'BodyStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#222222'), spaceAfter=5
)
cell_style = ParagraphStyle(
    'CellStyle', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#222222')
)
cell_header = ParagraphStyle(
    'CellHeader', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.whitesmoke, fontName='Helvetica-Bold'
)

story = []

# Titre
story.append(Paragraph("Rapport d'Investigation SOC — Incident Nordis", title_style))
story.append(Spacer(1, 5))

# 1. Synthèse
story.append(Paragraph("1. Synthèse Exécutive", h2_style))
story.append(Paragraph(
    "Entre le 11 et le 20 septembre 2026, l'entreprise a subi une cyberattaque majeure menant à la compromission du réseau, "
    "à l'exfiltration de <b>~853 Mo</b> de données comptables et au chiffrement des partages réseau (<code>SRV-FILE01</code>) par un rançongiciel. "
    "L'attaque a débuté par un hameçonnage (phishing), suivi d'un accès VPN illégitime, d'une élévation de privilèges (Admin du domaine) et de la suppression des sauvegardes.",
    body_style
))

# 2. Périmètre
story.append(Paragraph("2. Périmètre & Volumétrie", h2_style))
story.append(Paragraph("• <b>Période d'analyse :</b> 31 août 2026 (07:41) au 20 septembre 2026 (16:46)<br/>"
                       "• <b>Infrastructures :</b> 308 machines (300 postes, 8 serveurs sur les sites Siège, Lyon, Lille)<br/>"
                       "• <b>Sources analysées :</b> VPN, Mail, Proxy web, Active Directory, Pare-feu, EDR", body_style))

# 3. Chronologie
story.append(Paragraph("3. Chronologie de l'Attaque", h2_style))
story.append(Paragraph("<b>11/09 10:48 — Phishing :</b> Réception d'un mail piégé par <code>l.perrin</code> (poste <code>PC-SIE-1000</code>) depuis <code>comptabilite@fourniseur-x.example</code> avec un lien de typosquatting.<br/>"
                       "<b>11/09 23:17 — Accès VPN :</b> Connexion VPN réussie depuis l'IP <code>203.0.113.87</code> (Nigeria) avec le compte compromis.<br/>"
                       "<b>14/09 02:29 — Persistance AD :</b> Création du compte <code>svc_monitoring</code> et ajout au groupe <b>Admins du domaine</b>.<br/>"
                       "<b>19/09 03:43 — Exfiltration :</b> Transfert de 852,98 Mo vers <code>cloud-depot-securise.example</code> via le proxy.<br/>"
                       "<b>20/09 03:59 - 05:25 — Ransomware :</b> Arrêt des sauvegardes puis chiffrement massif de <code>SRV-FILE01</code>.", body_style))

# 4. Tableau Alertes EDR
story.append(Paragraph("4. Alertes EDR Ignorées", h2_style))

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

# 5. Recommandations
story.append(Paragraph("5. Recommandations Prioritaires", h2_style))
story.append(Paragraph("1. <b>Confinement :</b> Isoler <code>SRV-FILE01</code> et <code>PC-SIE-1000</code>, bloquer l'IP <code>203.0.113.87</code>.<br/>"
                       "2. <b>Assainissement AD :</b> Supprimer <code>svc_monitoring</code>, réinitialiser les mots de passe des comptes <code>l.perrin</code>, <code>n.vincent</code> et des admins.<br/>"
                       "3. <b>SOC / EDR :</b> Activer le blocage automatique pour les alertes EDR Critiques et imposer le MFA sur le VPN.", body_style))

doc.build(story)
print("PDF généré avec succès : Rapport_SOC_Investigation.pdf")
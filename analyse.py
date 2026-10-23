import pandas as pd
import json

with open('./donnees/edr_alerts.json', 'r', encoding='utf-8') as f:
    df_edr = pd.DataFrame(json.load(f))
df_edr['horodatage'] = pd.to_datetime(df_edr['horodatage'])

print("=== ALERTES EDR SUR LA MACHINE DE L.PERRIN OU APRES LE 11 SEPTEMBRE ===")
# On filtre sur l.perrin / PC-SIE-1000 ou sur la période de l'attaque
alertes_attaque = df_edr[(df_edr['utilisateur'] == 'l.perrin') | 
                         (df_edr['machine'] == 'PC-SIE-1000') | 
                         (df_edr['horodatage'] >= '2026-09-11')]

print(alertes_attaque[['horodatage', 'machine', 'utilisateur', 'titre', 'gravite', 'statut', 'note_analyste']].to_string())
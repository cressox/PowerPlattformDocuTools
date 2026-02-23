# Datenquellen

| Name | Typ | Verbindung | Aktualisierung | Gateway |
|---|---|---|---|---|
| SAP HR – Zeitkonten-View | SQL (SAP HANA) | redacted-host:0000 / Schema HR_REPORTING / View V_ZEITKONTEN | Täglich um redacted-host:0000 Uhr | OnPrem-Gateway-HR |
| Organisationsstruktur (Excel) | Excel (SharePoint) | SharePoint: /sites/HR/Shared Documents/Org_Struktur.xlsx | Wöchentlich (montags) | – |

## SAP HR – Zeitkonten-View

- **Typ:** SQL (SAP HANA)
- **Verbindung:** redacted-host:0000 / Schema HR_REPORTING / View V_ZEITKONTEN
- **Aktualisierung:** Täglich um redacted-host:0000 Uhr
- **Gateway:** Ja – OnPrem-Gateway-HR
- **Verantwortlich:** IT SAP Team (redacted@example.com)

---

## Organisationsstruktur (Excel)

- **Typ:** Excel (SharePoint)
- **Verbindung:** SharePoint: /sites/HR/Shared Documents/Org_Struktur.xlsx
- **Aktualisierung:** Wöchentlich (montags)
- **Gateway:** Nein
- **Verantwortlich:** HR Stammdaten (redacted@example.com)

---

# Datenquellen

| Name | Typ | Verbindung | Aktualisierung | Gateway |
|---|---|---|---|---|
| SAP HR – Zeitkonten-View | SQL (SAP HANA) | hana-host:30015 / Schema HR_REPORTING / View V_ZEITKONTEN | Täglich um 06:00 Uhr | OnPrem-Gateway-HR |
| Organisationsstruktur (Excel) | Excel (SharePoint) | SharePoint: /sites/HR/Shared Documents/Org_Struktur.xlsx | Wöchentlich (montags) | – |

## SAP HR – Zeitkonten-View

- **Typ:** SQL (SAP HANA)
- **Verbindung:** hana-host:30015 / Schema HR_REPORTING / View V_ZEITKONTEN
- **Aktualisierung:** Täglich um 06:00 Uhr
- **Gateway:** Ja – OnPrem-Gateway-HR
- **Verantwortlich:** IT SAP Team (sap-team@contoso.de)

---

## Organisationsstruktur (Excel)

- **Typ:** Excel (SharePoint)
- **Verbindung:** SharePoint: /sites/HR/Shared Documents/Org_Struktur.xlsx
- **Aktualisierung:** Wöchentlich (montags)
- **Gateway:** Nein
- **Verantwortlich:** HR Stammdaten (hr-stammdaten@contoso.de)

---

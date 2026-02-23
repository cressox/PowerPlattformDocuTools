# Governance – Aktualisierung, Gateway & RLS

## Aktualisierungsplan

Tägliche Aktualisierung um redacted-host:0000 Uhr via Power BI Service Scheduled Refresh. SAP-Daten werden um redacted-host:0000 via Gateway geladen.

## Monitoring

Refresh-Fehler werden per E-Mail an den Report-Owner gesendet. Zusätzlich Überwachung im Power BI Admin Portal.

## Row-Level Security (RLS)

RLS ist aktiviert: Teamleiter sehen nur Mitarbeiter ihrer Abteilung. HR Business Partner sehen alle Abteilungen ihres Bereichs. Rollen: Rolle_Teamleiter, Rolle_HRBP, Rolle_Admin.

## Performance-Hinweise

Bei >50.000 Zeitkontobuchungen kann die kumulative Saldo-Berechnung langsam werden. Ggf. vorberechnete Saldo-Spalte in Power Query erwägen.

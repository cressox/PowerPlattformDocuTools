# Variablen

| Name | Typ | Initialwert | Beschreibung | Gesetzt in | Verwendet in |
|---|---|---|---|---|---|
| VZeitStempelStatusAbgeschlossen | String | `` |  | VZeitStempelStatusAbgeschlossen |  |
| VZeitStempelAngebotErstellt | String | `` |  | VZeitStempelAngebotErstellt |  |
| VEndDatum | String | `@{utcNow()}` |  | VEndDatum |  |
| VTempCheckIfNull | String | `` |  | VTempCheckIfNull |  |
| VZeitStempelStatusAbgeschlossen | String | `@items('Check_Status_Abgeschlossen')?['OData___zeit_stempel_status_abgeschlos']` |  | Setze_VDatumStatusAbgeschlossen |  |
| VTempCheckIfNull | String | `@items('Check_Status_Abgeschlossen')?['OData___zeit_stempel_angebot_erstellt']` |  | Setze_VDatumAngebotErstellt |  |
| VZeitStempelAngebotErstellt | String | `@{if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))}` |  | Variable_festlegen |  |
| VTempCheckIfNull | String | `@items('Check_Status_Abgeschlossen')?['OData___zeit_stempel_angebot_erstellt']` |  | Setze_VDatumAngebotErstellt |  |
| VZeitStempelAngebotErstellt | String | `@{if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))}` |  | Variable_festlegen |  |
| VTempCheckIfNull | String | `@items('Check_Status_Abgeschlossen')?['OData___zeit_stempel_angebot_erstellt']` |  | Setze_VDatumAngebotErstellt |  |
| VZeitStempelAngebotErstellt | String | `@{if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))}` |  | Variable_festlegen |  |
| VTempCheckIfNull | String | `@items('Check_Status_Abgeschlossen')?['OData___zeit_stempel_angebot_erstellt']` |  | Setze_VDatumAngebotErstellt |  |
| VZeitStempelAngebotErstellt | String | `@{if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))}` |  | Variable_festlegen |  |


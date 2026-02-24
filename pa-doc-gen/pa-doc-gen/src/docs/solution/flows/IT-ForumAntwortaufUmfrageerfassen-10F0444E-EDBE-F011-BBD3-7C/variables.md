# Variablen

| Name | Typ | Initialwert | Beschreibung | Gesetzt in | Verwendet in |
|---|---|---|---|---|---|
| VVeranstaltungsJahr | String | `2026` |  | Initialize_variable |  |
| VPaketName | String | `""` |  | Variable_initialisieren |  |
| VPaketName | String | `@{coalesce(
    outputs('Antwortdetails_abrufen')?['body/r832b250258354e32ab45aacd520bdd64'],
    outputs('Antwortdetails_abrufen')?['body/ra218cfc51f1649f48432f222dc204a75'],
    outputs('Antwortdetails_abrufen')?['body/r952e6a0c2f95436ea5b2e1a5a763d86b'],
    'Standardwert oder Nachricht, wenn alle anderen leer sind'
)
}` |  | Variable_festlegen |  |
| VPaketName | String | `@{coalesce(
    outputs('Antwortdetails_abrufen')?['body/r832b250258354e32ab45aacd520bdd64'],
    outputs('Antwortdetails_abrufen')?['body/ra218cfc51f1649f48432f222dc204a75'],
    outputs('Antwortdetails_abrufen')?['body/r952e6a0c2f95436ea5b2e1a5a763d86b'],
    'Standardwert oder Nachricht, wenn alle anderen leer sind'
)
}` |  | Variable_festlegen |  |


# Flow-Struktur – Aktionen

## Aktionshierarchie

- **VZeitStempelStatusAbgeschlossen** *(InitializeVariable)*
- **VZeitStempelAngebotErstellt** *(InitializeVariable)*
  - Run After: SUCCEEDED
- **VEndDatum** *(InitializeVariable)*
  - Expression: `utcNow()`
  - Run After: SUCCEEDED
- **VTempCheckIfNull** *(InitializeVariable)*
  - Run After: SUCCEEDED
- **Elemente_abrufen_alle_Presales_Projekte** *(OpenApiConnection)* `[SharePoint]`
  - Run After: SUCCEEDED
- **Check_Status_Abgeschlossen** *(Foreach)*
  - Run After: SUCCEEDED
  - **Setze_VDatumStatusAbgeschlossen** *(SetVariable)*
  - **Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null** *(If)*
    - Run After: Succeeded
    - **Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt** *(If)*
      - **Setze_VDatumAngebotErstellt** *(SetVariable)*
      - **Variable_festlegen** *(SetVariable)*
        - Expression: `if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))`
        - Run After: Succeeded
      - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen** *(If)*
        - Run After: Succeeded
        - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
          - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
        - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja** *(Branch_True)*
          - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
            - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
        - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein** *(Branch_False)*
          - **Auftrag_gewonnen** *(If)*
            - **Auftragsnummer_bekannt** *(If)*
              - **Auftragsnummer_bekannt – Nein** *(Branch_False)*
                - **E-Mail_senden_(V2)_3** *(OpenApiConnection)* `[Office 365 Outlook]`
                  - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
            - **Auftrag_gewonnen – Ja** *(Branch_True)*
              - **Auftragsnummer_bekannt** *(If)*
                - **Auftragsnummer_bekannt – Nein** *(Branch_False)*
                  - **E-Mail_senden_(V2)_3** *(OpenApiConnection)* `[Office 365 Outlook]`
                    - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
      - **Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja** *(Branch_True)*
        - **Setze_VDatumAngebotErstellt** *(SetVariable)*
        - **Variable_festlegen** *(SetVariable)*
          - Expression: `if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))`
          - Run After: Succeeded
        - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen** *(If)*
          - Run After: Succeeded
          - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
            - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
          - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja** *(Branch_True)*
            - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
              - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
          - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein** *(Branch_False)*
            - **Auftrag_gewonnen** *(If)*
              - **Auftragsnummer_bekannt** *(If)*
                - **Auftragsnummer_bekannt – Nein** *(Branch_False)*
                  - **E-Mail_senden_(V2)_3** *(OpenApiConnection)* `[Office 365 Outlook]`
                    - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
              - **Auftrag_gewonnen – Ja** *(Branch_True)*
                - **Auftragsnummer_bekannt** *(If)*
                  - **Auftragsnummer_bekannt – Nein** *(Branch_False)*
                    - **E-Mail_senden_(V2)_3** *(OpenApiConnection)* `[Office 365 Outlook]`
                      - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
      - **Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein** *(Branch_False)*
        - **Angebot_noch_offen** *(If)*
          - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
            - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
          - **Angebot_noch_offen – Ja** *(Branch_True)*
            - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
              - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
    - **Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null – Ja** *(Branch_True)*
      - **Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt** *(If)*
        - **Setze_VDatumAngebotErstellt** *(SetVariable)*
        - **Variable_festlegen** *(SetVariable)*
          - Expression: `if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))`
          - Run After: Succeeded
        - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen** *(If)*
          - Run After: Succeeded
          - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
            - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
          - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja** *(Branch_True)*
            - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
              - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
          - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein** *(Branch_False)*
            - **Auftrag_gewonnen** *(If)*
              - **Auftragsnummer_bekannt** *(If)*
                - **Auftragsnummer_bekannt – Nein** *(Branch_False)*
                  - **E-Mail_senden_(V2)_3** *(OpenApiConnection)* `[Office 365 Outlook]`
                    - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
              - **Auftrag_gewonnen – Ja** *(Branch_True)*
                - **Auftragsnummer_bekannt** *(If)*
                  - **Auftragsnummer_bekannt – Nein** *(Branch_False)*
                    - **E-Mail_senden_(V2)_3** *(OpenApiConnection)* `[Office 365 Outlook]`
                      - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
        - **Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja** *(Branch_True)*
          - **Setze_VDatumAngebotErstellt** *(SetVariable)*
          - **Variable_festlegen** *(SetVariable)*
            - Expression: `if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))`
            - Run After: Succeeded
          - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen** *(If)*
            - Run After: Succeeded
            - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
              - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
            - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja** *(Branch_True)*
              - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
                - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
            - **Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein** *(Branch_False)*
              - **Auftrag_gewonnen** *(If)*
                - **Auftragsnummer_bekannt** *(If)*
                  - **Auftragsnummer_bekannt – Nein** *(Branch_False)*
                    - **E-Mail_senden_(V2)_3** *(OpenApiConnection)* `[Office 365 Outlook]`
                      - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
                - **Auftrag_gewonnen – Ja** *(Branch_True)*
                  - **Auftragsnummer_bekannt** *(If)*
                    - **Auftragsnummer_bekannt – Nein** *(Branch_False)*
                      - **E-Mail_senden_(V2)_3** *(OpenApiConnection)* `[Office 365 Outlook]`
                        - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
        - **Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein** *(Branch_False)*
          - **Angebot_noch_offen** *(If)*
            - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
              - Expression: `items('Check_Status_Abgeschlossen')?['Title']`
            - **Angebot_noch_offen – Ja** *(Branch_True)*
              - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
                - Expression: `items('Check_Status_Abgeschlossen')?['Title']`

---

## Aktionen im Detail


### VZeitStempelStatusAbgeschlossen

| Eigenschaft | Wert |
|---|---|
| Typ | `InitializeVariable` |

### VZeitStempelAngebotErstellt

| Eigenschaft | Wert |
|---|---|
| Typ | `InitializeVariable` |
| Run After | SUCCEEDED |

### VEndDatum

| Eigenschaft | Wert |
|---|---|
| Typ | `InitializeVariable` |
| Run After | SUCCEEDED |

**Expression:**
```
utcNow()
```


### VTempCheckIfNull

| Eigenschaft | Wert |
|---|---|
| Typ | `InitializeVariable` |
| Run After | SUCCEEDED |

### Elemente_abrufen_alle_Presales_Projekte

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |
| Run After | SUCCEEDED |

### Check_Status_Abgeschlossen

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |
| Run After | SUCCEEDED |

#### Setze_VDatumStatusAbgeschlossen

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

#### Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | Succeeded |

##### Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Setze_VDatumAngebotErstellt

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

###### Variable_festlegen

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |
| Run After | Succeeded |

**Expression:**
```
if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | Succeeded |

###### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### Auftrag_gewonnen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### E-Mail_senden_(V2)_3

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
items('Check_Status_Abgeschlossen')?['{Link
```


###### Auftrag_gewonnen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### Auftragsnummer_bekannt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### E-Mail_senden_(V2)_3

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
items('Check_Status_Abgeschlossen')?['{Link
```


###### Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### Setze_VDatumAngebotErstellt

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

###### Variable_festlegen

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |
| Run After | Succeeded |

**Expression:**
```
if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | Succeeded |

###### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### Auftrag_gewonnen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### E-Mail_senden_(V2)_3

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
items('Check_Status_Abgeschlossen')?['{Link
```


###### Auftrag_gewonnen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### Auftragsnummer_bekannt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### E-Mail_senden_(V2)_3

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
items('Check_Status_Abgeschlossen')?['{Link
```


###### Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### Angebot_noch_offen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelStatusAbgeschlossen'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelStatusAbgeschlossen'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_noch_offen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelStatusAbgeschlossen'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelStatusAbgeschlossen'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


##### Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Setze_VDatumAngebotErstellt

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

###### Variable_festlegen

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |
| Run After | Succeeded |

**Expression:**
```
if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | Succeeded |

###### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### Auftrag_gewonnen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### E-Mail_senden_(V2)_3

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
items('Check_Status_Abgeschlossen')?['{Link
```


###### Auftrag_gewonnen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### Auftragsnummer_bekannt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### E-Mail_senden_(V2)_3

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
items('Check_Status_Abgeschlossen')?['{Link
```


###### Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### Setze_VDatumAngebotErstellt

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

###### Variable_festlegen

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |
| Run After | Succeeded |

**Expression:**
```
if(equals(variables('VTempCheckIfNull'), null), utcNow(), variables('VTempCheckIfNull'))
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | Succeeded |

###### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelAngebotErstellt'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### Auftrag_gewonnen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### E-Mail_senden_(V2)_3

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
items('Check_Status_Abgeschlossen')?['{Link
```


###### Auftrag_gewonnen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### Auftragsnummer_bekannt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### Auftragsnummer_bekannt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### E-Mail_senden_(V2)_3

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
items('Check_Status_Abgeschlossen')?['{Link
```


###### Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

###### Angebot_noch_offen

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

###### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelStatusAbgeschlossen'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelStatusAbgeschlossen'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```


###### Angebot_noch_offen – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Check_Status_Abgeschlossen')?['Title']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelStatusAbgeschlossen'))),864000000000)
items('Check_Status_Abgeschlossen')?['Author/DisplayName']
items('Check_Status_Abgeschlossen')?['Title']
item()?['Kundenname']
div(sub(ticks(variables('VEndDatum')),ticks(variables('VZeitStempelStatusAbgeschlossen'))),864000000000)
items('Check_Status_Abgeschlossen')?['{Link
```



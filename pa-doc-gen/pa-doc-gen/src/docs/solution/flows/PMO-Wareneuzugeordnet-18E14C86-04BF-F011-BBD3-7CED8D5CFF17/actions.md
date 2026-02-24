# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Änderungen_für_ein_Element_oder_eine_Datei_abrufen_(nur_Eigenschaften)** *(OpenApiConnection)* `[SharePoint]`
- **Bedingung** *(If)*
  - Run After: Succeeded
  - **Elemente_abrufen** *(OpenApiConnection)* `[SharePoint]`
    - Expression: `triggerOutputs()?['body/Auftragsnummer']`
  - **Auf_alle_anwenden** *(Foreach)*
    - Run After: Succeeded
    - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
      - Expression: `items('Auf_alle_anwenden')?['Projektname2']`
  - **Bedingung – Ja** *(Branch_True)*
    - **Elemente_abrufen** *(OpenApiConnection)* `[SharePoint]`
      - Expression: `triggerOutputs()?['body/Auftragsnummer']`
    - **Auf_alle_anwenden** *(Foreach)*
      - Run After: Succeeded
      - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
        - Expression: `items('Auf_alle_anwenden')?['Projektname2']`

---

## Aktionen im Detail


### Änderungen_für_ein_Element_oder_eine_Datei_abrufen_(nur_Eigenschaften)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

### Bedingung

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | Succeeded |

#### Elemente_abrufen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

**Expression:**
```
triggerOutputs()?['body/Auftragsnummer']
```


#### Auf_alle_anwenden

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |
| Run After | Succeeded |

##### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Auf_alle_anwenden')?['Projektname2']
items('Auf_alle_anwenden')?['Projektleiter/DisplayName']
items('Auf_alle_anwenden')?['Projektname2']
triggerOutputs()?['body/Auftragsnummer']
triggerOutputs()?['body/Eingangsdatum']
triggerOutputs()?['body/Lagerortcode']
triggerOutputs()?['body/Kommentar']
```


#### Bedingung – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

##### Elemente_abrufen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

**Expression:**
```
triggerOutputs()?['body/Auftragsnummer']
```


##### Auf_alle_anwenden

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |
| Run After | Succeeded |

###### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
items('Auf_alle_anwenden')?['Projektname2']
items('Auf_alle_anwenden')?['Projektleiter/DisplayName']
items('Auf_alle_anwenden')?['Projektname2']
triggerOutputs()?['body/Auftragsnummer']
triggerOutputs()?['body/Eingangsdatum']
triggerOutputs()?['body/Lagerortcode']
triggerOutputs()?['body/Kommentar']
```



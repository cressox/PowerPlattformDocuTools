# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Antwortdetails_abrufen** *(OpenApiConnection)* `[shared_microsoftforms]`
- **Element_erstellen** *(OpenApiConnection)* `[SharePoint]`
  - Expression: `triggerOutputs()?['body/resourceData/responseId']`
  - Run After: SUCCEEDED
- **Verfassen** *(Compose)*
  - Run After: SUCCEEDED
- **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
  - Expression: `if(equals(body('Antwortdetails_abrufen')?['r0722a748604646b3a29f7019eb0f771d'], 'Hund'), 'Ein', 'Eine')`
  - Run After: SUCCEEDED

---

## Aktionen im Detail


### Antwortdetails_abrufen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | shared_microsoftforms |

### Element_erstellen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |
| Run After | SUCCEEDED |

**Expression:**
```
triggerOutputs()?['body/resourceData/responseId']
```


### Verfassen

| Eigenschaft | Wert |
|---|---|
| Typ | `Compose` |
| Run After | SUCCEEDED |

### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |
| Run After | SUCCEEDED |

**Expression:**
```
if(equals(body('Antwortdetails_abrufen')?['r0722a748604646b3a29f7019eb0f771d'], 'Hund'), 'Ein', 'Eine')
body('Antwortdetails_abrufen')?['rc2159fb1ba994d88b375071213cbaab2']
if(equals(body('Antwortdetails_abrufen')?['r0722a748604646b3a29f7019eb0f771d'], 'Hund'), 'er', 'e')
body('Antwortdetails_abrufen')?['r0722a748604646b3a29f7019eb0f771d']
body('Antwortdetails_abrufen')?['r4a8cf85e201245bdb69ed38ba945ecb8']
if(or(equals(body('Element_erstellen')?['Wiewahrscheinlichistes_x002c_das'], 'Personalwesen'), equals(body('Element_erstellen')?['Wiewahrscheinlichistes_x002c_das'], 'Vertrieb')),'im', 'in der')
body('Antwortdetails_abrufen')?['rea8cac56d3794d3a9c6ff3f896bb712c']
```



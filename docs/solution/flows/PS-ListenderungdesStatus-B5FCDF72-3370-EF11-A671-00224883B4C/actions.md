# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Änderungen_für_ein_Element_oder_eine_Datei_abrufen_(nur_Eigenschaften)** *(OpenApiConnection)* `[SharePoint]`
- **Bedingung** *(If)*
  - Run After: Succeeded
  - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
    - Expression: `triggerOutputs()?['body/Title']`
  - **Bedingung – Ja** *(Branch_True)*
    - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
      - Expression: `triggerOutputs()?['body/Title']`

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

#### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
triggerOutputs()?['body/Title']
triggerOutputs()?['body/Editor/DisplayName']
triggerOutputs()?['body/{Link
triggerOutputs()?['body/Status']
```


#### Bedingung – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

##### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
triggerOutputs()?['body/Title']
triggerOutputs()?['body/Editor/DisplayName']
triggerOutputs()?['body/{Link
triggerOutputs()?['body/Status']
```



# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Scope** *(Scope)*
  - **Update_item** *(OpenApiConnection)* `[SharePoint]`
  - **Send_an_email_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
    - Expression: `triggerOutputs()?['body/Title']`
    - Run After: SUCCEEDED
  - **Send_an_email_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
    - Expression: `outputs('Update_item')?['body/ToSee_x002e_/DisplayName']`
    - Run After: SUCCEEDED

---

## Aktionen im Detail


### Scope

| Eigenschaft | Wert |
|---|---|
| Typ | `Scope` |

#### Update_item

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

#### Send_an_email_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |
| Run After | SUCCEEDED |

**Expression:**
```
triggerOutputs()?['body/Title']
outputs('Update_item')?['body/Name']
outputs('Update_item')?['body/Timein']
outputs('Update_item')?['body/ToSee_x002e_/DisplayName']
```


#### Send_an_email_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |
| Run After | SUCCEEDED |

**Expression:**
```
outputs('Update_item')?['body/ToSee_x002e_/DisplayName']
outputs('Update_item')?['body/Title']
outputs('Update_item')?['body/Name']
outputs('Update_item')?['body/Timein']
outputs('Update_item')?['body/Title']
```



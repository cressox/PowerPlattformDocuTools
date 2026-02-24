# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Get_changes_for_an_item_or_a_file_(properties_only)** *(OpenApiConnection)* `[SharePoint]`
- **Condition** *(If)*
  - Run After: SUCCEEDED
  - **Send_an_email_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
    - Expression: `triggerBody()?['Title']`
  - **Condition – Ja** *(Branch_True)*
    - **Send_an_email_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
      - Expression: `triggerBody()?['Title']`

---

## Aktionen im Detail


### Get_changes_for_an_item_or_a_file_(properties_only)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

### Condition

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | SUCCEEDED |

#### Send_an_email_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
triggerBody()?['Title']
triggerBody()?['{Link
triggerBody()?['Link_x0020_zur_x0020_Kundenakte']
triggerBody()?['Projektleiter/Claims']
triggerBody()?['VB/Claims']
triggerBody()?['VI/Claims']
```


#### Condition – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

##### Send_an_email_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
triggerBody()?['Title']
triggerBody()?['{Link
triggerBody()?['Link_x0020_zur_x0020_Kundenakte']
triggerBody()?['Projektleiter/Claims']
triggerBody()?['VB/Claims']
triggerBody()?['VI/Claims']
```



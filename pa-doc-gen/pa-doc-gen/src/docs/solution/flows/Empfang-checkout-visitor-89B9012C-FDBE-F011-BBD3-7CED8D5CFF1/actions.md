# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Bedingung** *(If)*
  - **Elemente_abrufen** *(OpenApiConnection)* `[SharePoint]`
    - Expression: `trim(replace(triggerOutputs()?['body/subject'], 'Ausschecken', ''))`
  - **Auf_alle_anwenden** *(Foreach)*
    - Run After: Succeeded
    - **Element_aktualisieren** *(OpenApiConnection)* `[SharePoint]`
  - **Bedingung – Ja** *(Branch_True)*
    - **Elemente_abrufen** *(OpenApiConnection)* `[SharePoint]`
      - Expression: `trim(replace(triggerOutputs()?['body/subject'], 'Ausschecken', ''))`
    - **Auf_alle_anwenden** *(Foreach)*
      - Run After: Succeeded
      - **Element_aktualisieren** *(OpenApiConnection)* `[SharePoint]`

---

## Aktionen im Detail


### Bedingung

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

#### Elemente_abrufen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

**Expression:**
```
trim(replace(triggerOutputs()?['body/subject'], 'Ausschecken', ''))
```


#### Auf_alle_anwenden

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |
| Run After | Succeeded |

##### Element_aktualisieren

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

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
trim(replace(triggerOutputs()?['body/subject'], 'Ausschecken', ''))
```


##### Auf_alle_anwenden

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |
| Run After | Succeeded |

###### Element_aktualisieren

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |


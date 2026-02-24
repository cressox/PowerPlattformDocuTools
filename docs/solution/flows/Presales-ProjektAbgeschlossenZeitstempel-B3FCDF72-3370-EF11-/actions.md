# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Änderungen_für_ein_Element_oder_eine_Datei_abrufen_(nur_Eigenschaften)** *(OpenApiConnection)* `[SharePoint]`
- **Bedingung** *(If)*
  - Run After: Succeeded
  - **Auf_alle_anwenden** *(Foreach)*
    - **Element_Aktualisieren_-_Setzte_Zeitstempel** *(OpenApiConnection)* `[SharePoint]`
  - **Bedingung – Ja** *(Branch_True)*
    - **Auf_alle_anwenden** *(Foreach)*
      - **Element_Aktualisieren_-_Setzte_Zeitstempel** *(OpenApiConnection)* `[SharePoint]`
- **Catch_Error** *(Scope)*
  - Run After: Failed, Skipped, TimedOut
  - **Parse_JSON** *(ParseJson)*

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

#### Auf_alle_anwenden

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |

##### Element_Aktualisieren_-_Setzte_Zeitstempel

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

#### Bedingung – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

##### Auf_alle_anwenden

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |

###### Element_Aktualisieren_-_Setzte_Zeitstempel

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

### Catch_Error

| Eigenschaft | Wert |
|---|---|
| Typ | `Scope` |
| Run After | Failed, Skipped, TimedOut |

#### Parse_JSON

| Eigenschaft | Wert |
|---|---|
| Typ | `ParseJson` |


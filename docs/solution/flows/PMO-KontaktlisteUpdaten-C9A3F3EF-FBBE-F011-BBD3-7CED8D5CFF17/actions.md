# Flow-Struktur – Aktionen

## Aktionshierarchie

- **HTTP-Anforderung_senden** *(OpenApiConnection)* `[Office 365 Outlook]`
- **Variable_initialisieren** *(InitializeVariable)*
  - Run After: Succeeded
- **Array_filtern** *(Query)*
  - Run After: Succeeded
- **JSON_analysieren** *(ParseJson)*
  - Run After: Succeeded
- **Elemente_abrufen** *(OpenApiConnection)* `[SharePoint]`
  - Run After: Succeeded
- **For_each_SP** *(Foreach)*
  - Run After: Succeeded
  - **Element_löschen** *(OpenApiConnection)* `[SharePoint]`
- **For_each_O365** *(Foreach)*
  - Run After: Succeeded
  - **Benutzerprofil_abrufen_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
  - **Element_erstellen** *(OpenApiConnection)* `[SharePoint]`
    - Run After: Succeeded

---

## Aktionen im Detail


### HTTP-Anforderung_senden

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

### Variable_initialisieren

| Eigenschaft | Wert |
|---|---|
| Typ | `InitializeVariable` |
| Run After | Succeeded |

### Array_filtern

| Eigenschaft | Wert |
|---|---|
| Typ | `Query` |
| Run After | Succeeded |

### JSON_analysieren

| Eigenschaft | Wert |
|---|---|
| Typ | `ParseJson` |
| Run After | Succeeded |

### Elemente_abrufen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |
| Run After | Succeeded |

### For_each_SP

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |
| Run After | Succeeded |

#### Element_löschen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

### For_each_O365

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |
| Run After | Succeeded |

#### Benutzerprofil_abrufen_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

#### Element_erstellen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |
| Run After | Succeeded |


# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Initialize_variable** *(InitializeVariable)*
- **Variable_initialisieren** *(InitializeVariable)*
  - Run After: SUCCEEDED
- **Antwortdetails_abrufen** *(OpenApiConnection)* `[shared_microsoftforms]`
  - Run After: SUCCEEDED
- **Absage** *(If)*
  - Run After: SUCCEEDED
  - **Variable_festlegen** *(SetVariable)*
    - Expression: `@{coalesce(`
  - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
    - Expression: `outputs('Antwortdetails_abrufen')?['body/r3715ec9e2fc3420593d312df3f6198fd']`
    - Run After: SUCCEEDED
  - **Absage – Ja** *(Branch_True)*
    - **Variable_festlegen** *(SetVariable)*
      - Expression: `@{coalesce(`
    - **E-Mail_senden_(V2)** *(OpenApiConnection)* `[Office 365 Outlook]`
      - Expression: `outputs('Antwortdetails_abrufen')?['body/r3715ec9e2fc3420593d312df3f6198fd']`
      - Run After: SUCCEEDED
  - **Absage – Nein** *(Branch_False)*
    - **E-Mail_senden_(V2)_2** *(OpenApiConnection)* `[Office 365 Outlook]`
      - Expression: `outputs('Antwortdetails_abrufen')?['body/r3715ec9e2fc3420593d312df3f6198fd']`

---

## Aktionen im Detail


### Initialize_variable

| Eigenschaft | Wert |
|---|---|
| Typ | `InitializeVariable` |

### Variable_initialisieren

| Eigenschaft | Wert |
|---|---|
| Typ | `InitializeVariable` |
| Run After | SUCCEEDED |

### Antwortdetails_abrufen

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | shared_microsoftforms |
| Run After | SUCCEEDED |

### Absage

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | SUCCEEDED |

#### Variable_festlegen

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

**Expression:**
```
@{coalesce(
    outputs('Antwortdetails_abrufen')?['body/r832b250258354e32ab45aacd520bdd64'],
    outputs('Antwortdetails_abrufen')?['body/ra218cfc51f1649f48432f222dc204a75'],
    outputs('Antwortdetails_abrufen')?['body/r952e6a0c2f95436ea5b2e1a5a763d86b'],
    'Standardwert oder Nachricht, wenn alle anderen leer sind'
)
}
```


#### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |
| Run After | SUCCEEDED |

**Expression:**
```
outputs('Antwortdetails_abrufen')?['body/r3715ec9e2fc3420593d312df3f6198fd']
variables('VVeranstaltungsJahr')
variables('VVeranstaltungsJahr')
outputs('Antwortdetails_abrufen')?['body/r9aedbea381c84e48b7b0b2c4dac0650d']
outputs('Antwortdetails_abrufen')?['body/r83f38aff8e9b4a84bb3acd7aea884754']
outputs('Antwortdetails_abrufen')?['body/r35c2982d14764743ab88c7e147d866db']
outputs('Antwortdetails_abrufen')?['body/r832b250258354e32ab45aacd520bdd64']
outputs('Antwortdetails_abrufen')?['body/ra218cfc51f1649f48432f222dc204a75']
outputs('Antwortdetails_abrufen')?['body/r952e6a0c2f95436ea5b2e1a5a763d86b']
outputs('Antwortdetails_abrufen')?['body/r4aa313149e75450a9662af94e1341c93']
outputs('Antwortdetails_abrufen')?['body/r9482c53838184d66bad7f1fdc5c521af']
outputs('Antwortdetails_abrufen')?['body/r21bd9954303e4f4a8390aac4a3110ea8']
outputs('Antwortdetails_abrufen')?['body/r01b46995ed304722b933f6e36c428239']
outputs('Antwortdetails_abrufen')?['body/r62922f0a4ba7491bada26bf33ef505dd']
outputs('Antwortdetails_abrufen')?['body/r6aef464b462743a6beb4f369360016ce']
outputs('Antwortdetails_abrufen')?['body/r88be61c4d27847e48a2401243cb445a9']
outputs('Antwortdetails_abrufen')?['body/r60b532d2f4d94477b1a3f6b1d2864d24']
outputs('Antwortdetails_abrufen')?['body/rb58f45ecc97446ff940de53c3b238c8a']
outputs('Antwortdetails_abrufen')?['body/r9f6f34cd219248c4ae4f059904be00ff']
outputs('Antwortdetails_abrufen')?['body/rcada3cf6eb974f3f91417b1bbe84bbac']
outputs('Antwortdetails_abrufen')?['body/r771e4b3b4a7346c6b5bcedb62dc0de3a']
outputs('Antwortdetails_abrufen')?['body/rb59ff662941b499d97d253543c095f73']
outputs('Antwortdetails_abrufen')?['body/rcd3f6514ad1749d4824485ffb657e8c8']
outputs('Antwortdetails_abrufen')?['body/r7247d67f18b84103a1185b61da0c37d8']
outputs('Antwortdetails_abrufen')?['body/rfa8ace3a1146438b8fda3da6a0ca9bd5']
outputs('Antwortdetails_abrufen')?['body/r27df4c83cc0343abaa9f4c6858fef7e7']
outputs('Antwortdetails_abrufen')?['body/r27df4c83cc0343abaa9f4c6858fef7e7']
outputs('Antwortdetails_abrufen')?['body/r0bb2dab4c8d04ac5895642d1e4cbbcf9']
outputs('Antwortdetails_abrufen')?['body/re23d4cf3920b4923b965140b9f7b059e']
outputs('Antwortdetails_abrufen')?['body/r264a6fb82bfa49849bad77372770b91c']
outputs('Antwortdetails_abrufen')?['body/r03c4550d707846b09f069c00f1359f1d']
outputs('Antwortdetails_abrufen')?['body/r83f38aff8e9b4a84bb3acd7aea884754']
outputs('Antwortdetails_abrufen')?['body/r301ecf1e868c4848a611e16f0e75bbfc']
outputs('Antwortdetails_abrufen')?['body/r9fc5e393d7cf4509a157a6ff83634ff9']
outputs('Antwortdetails_abrufen')?['body/r2e05e8851d824581affbd1ce70673e66']
outputs('Antwortdetails_abrufen')?['body/r6a8a1efd59a149ecb923ec524b6a6a3a']
outputs('Antwortdetails_abrufen')?['body/r6db3e86b61564751bc953b4a036c44b6']
variables('VVeranstaltungsJahr')
```


#### Absage – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

##### Variable_festlegen

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

**Expression:**
```
@{coalesce(
    outputs('Antwortdetails_abrufen')?['body/r832b250258354e32ab45aacd520bdd64'],
    outputs('Antwortdetails_abrufen')?['body/ra218cfc51f1649f48432f222dc204a75'],
    outputs('Antwortdetails_abrufen')?['body/r952e6a0c2f95436ea5b2e1a5a763d86b'],
    'Standardwert oder Nachricht, wenn alle anderen leer sind'
)
}
```


##### E-Mail_senden_(V2)

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |
| Run After | SUCCEEDED |

**Expression:**
```
outputs('Antwortdetails_abrufen')?['body/r3715ec9e2fc3420593d312df3f6198fd']
variables('VVeranstaltungsJahr')
variables('VVeranstaltungsJahr')
outputs('Antwortdetails_abrufen')?['body/r9aedbea381c84e48b7b0b2c4dac0650d']
outputs('Antwortdetails_abrufen')?['body/r83f38aff8e9b4a84bb3acd7aea884754']
outputs('Antwortdetails_abrufen')?['body/r35c2982d14764743ab88c7e147d866db']
outputs('Antwortdetails_abrufen')?['body/r832b250258354e32ab45aacd520bdd64']
outputs('Antwortdetails_abrufen')?['body/ra218cfc51f1649f48432f222dc204a75']
outputs('Antwortdetails_abrufen')?['body/r952e6a0c2f95436ea5b2e1a5a763d86b']
outputs('Antwortdetails_abrufen')?['body/r4aa313149e75450a9662af94e1341c93']
outputs('Antwortdetails_abrufen')?['body/r9482c53838184d66bad7f1fdc5c521af']
outputs('Antwortdetails_abrufen')?['body/r21bd9954303e4f4a8390aac4a3110ea8']
outputs('Antwortdetails_abrufen')?['body/r01b46995ed304722b933f6e36c428239']
outputs('Antwortdetails_abrufen')?['body/r62922f0a4ba7491bada26bf33ef505dd']
outputs('Antwortdetails_abrufen')?['body/r6aef464b462743a6beb4f369360016ce']
outputs('Antwortdetails_abrufen')?['body/r88be61c4d27847e48a2401243cb445a9']
outputs('Antwortdetails_abrufen')?['body/r60b532d2f4d94477b1a3f6b1d2864d24']
outputs('Antwortdetails_abrufen')?['body/rb58f45ecc97446ff940de53c3b238c8a']
outputs('Antwortdetails_abrufen')?['body/r9f6f34cd219248c4ae4f059904be00ff']
outputs('Antwortdetails_abrufen')?['body/rcada3cf6eb974f3f91417b1bbe84bbac']
outputs('Antwortdetails_abrufen')?['body/r771e4b3b4a7346c6b5bcedb62dc0de3a']
outputs('Antwortdetails_abrufen')?['body/rb59ff662941b499d97d253543c095f73']
outputs('Antwortdetails_abrufen')?['body/rcd3f6514ad1749d4824485ffb657e8c8']
outputs('Antwortdetails_abrufen')?['body/r7247d67f18b84103a1185b61da0c37d8']
outputs('Antwortdetails_abrufen')?['body/rfa8ace3a1146438b8fda3da6a0ca9bd5']
outputs('Antwortdetails_abrufen')?['body/r27df4c83cc0343abaa9f4c6858fef7e7']
outputs('Antwortdetails_abrufen')?['body/r27df4c83cc0343abaa9f4c6858fef7e7']
outputs('Antwortdetails_abrufen')?['body/r0bb2dab4c8d04ac5895642d1e4cbbcf9']
outputs('Antwortdetails_abrufen')?['body/re23d4cf3920b4923b965140b9f7b059e']
outputs('Antwortdetails_abrufen')?['body/r264a6fb82bfa49849bad77372770b91c']
outputs('Antwortdetails_abrufen')?['body/r03c4550d707846b09f069c00f1359f1d']
outputs('Antwortdetails_abrufen')?['body/r83f38aff8e9b4a84bb3acd7aea884754']
outputs('Antwortdetails_abrufen')?['body/r301ecf1e868c4848a611e16f0e75bbfc']
outputs('Antwortdetails_abrufen')?['body/r9fc5e393d7cf4509a157a6ff83634ff9']
outputs('Antwortdetails_abrufen')?['body/r2e05e8851d824581affbd1ce70673e66']
outputs('Antwortdetails_abrufen')?['body/r6a8a1efd59a149ecb923ec524b6a6a3a']
outputs('Antwortdetails_abrufen')?['body/r6db3e86b61564751bc953b4a036c44b6']
variables('VVeranstaltungsJahr')
```


#### Absage – Nein

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_False` |

##### E-Mail_senden_(V2)_2

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | Office 365 Outlook |

**Expression:**
```
outputs('Antwortdetails_abrufen')?['body/r3715ec9e2fc3420593d312df3f6198fd']
outputs('Antwortdetails_abrufen')?['body/r83f38aff8e9b4a84bb3acd7aea884754']
variables('VVeranstaltungsJahr')
variables('VVeranstaltungsJahr')
variables('VVeranstaltungsJahr')
outputs('Antwortdetails_abrufen')?['body/r3715ec9e2fc3420593d312df3f6198fd']
variables('VVeranstaltungsJahr')
```



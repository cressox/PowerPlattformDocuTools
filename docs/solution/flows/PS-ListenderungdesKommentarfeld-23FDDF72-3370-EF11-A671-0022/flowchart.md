# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ Wenn_ein_Element_oder_eine_Datei_geändert_wird\n[SharePoint]\n(Recurrence)"])
    nderungen_f_r_ein_Element_oder_eine_Datei_abrufen__2080["Änderungen_für_ein_Element_oder_eine_Datei_abrufen_(nur_Eigenschaften)\n[SharePoint]"]
    TRIGGER --> nderungen_f_r_ein_Element_oder_eine_Datei_abrufen__2080
    Bedingung_1632{{"Bedingung"}}
    nderungen_f_r_ein_Element_oder_eine_Datei_abrufen__2080 --> Bedingung_1632
    Bedingung_Ja_2304(["Bedingung – Ja"])
    Bedingung_1632 -->|Ja| Bedingung_Ja_2304
    E_Mail_senden_V2_2976["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Bedingung_Ja_2304 --> E_Mail_senden_V2_2976
    E_Mail_senden_V2_2528["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Bedingung_1632 --> E_Mail_senden_V2_2528
    FLOW_END(["Ende"])
    E_Mail_senden_V2_2976 --> FLOW_END
    E_Mail_senden_V2_2528 --> FLOW_END

    class TRIGGER trigger
    class nderungen_f_r_ein_Element_oder_eine_Datei_abrufen__2080 connector
    class Bedingung_1632 condition
    class Bedingung_Ja_2304 branch_true
    class E_Mail_senden_V2_2976 connector
    class E_Mail_senden_V2_2528 connector
    class FLOW_END terminate

    %% Styles
    classDef trigger fill:#5B8DEF,stroke:#3A6FD8,color:#fff,stroke-width:2px
    classDef action fill:#1E2233,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px
    classDef connector fill:#1A3A5C,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px
    classDef condition fill:#E0A526,stroke:#C48F20,color:#fff,stroke-width:2px
    classDef loop fill:#9C27B0,stroke:#7B1FA2,color:#fff,stroke-width:2px
    classDef scope fill:#2E3B4E,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px,stroke-dasharray: 5 5
    classDef branch_true fill:#4CAF50,stroke:#388E3C,color:#fff,stroke-width:1px
    classDef branch_false fill:#EF5B5B,stroke:#D32F2F,color:#fff,stroke-width:1px
    classDef variable fill:#00897B,stroke:#00695C,color:#fff,stroke-width:1px
    classDef data fill:#546E7A,stroke:#37474F,color:#fff,stroke-width:1px
    classDef http fill:#FF7043,stroke:#E64A19,color:#fff,stroke-width:1px
    classDef terminate fill:#EF5B5B,stroke:#D32F2F,color:#fff,stroke-width:2px
```


### Legende

| Farbe | Bedeutung |
|---|---|
| 🔵 Blau | Trigger / Standard-Aktion |
| 🟡 Gelb | Bedingung (If/Switch) |
| 🟣 Lila | Schleife (Foreach/Until) |
| 🟢 Gruen | Ja-Zweig / Case |
| 🔴 Rot | Nein-Zweig / Default / Ende |
| 🟤 Orange | HTTP-Aktionen |
| 🔷 Tuerkis | Variablen-Aktionen |
| ⬜ Grau | Daten-Operationen (Compose, ParseJson) |


# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ Recurrence\n(Recurrence)"])
    HTTP_Anforderung_senden_2304["HTTP-Anforderung_senden\n[Office 365 Outlook]"]
    TRIGGER --> HTTP_Anforderung_senden_2304
    Variable_initialisieren_9168["Variable_initialisieren"]
    HTTP_Anforderung_senden_2304 --> Variable_initialisieren_9168
    Array_filtern_1856["Array_filtern"]
    Variable_initialisieren_9168 --> Array_filtern_1856
    JSON_analysieren_2528["JSON_analysieren"]
    Array_filtern_1856 --> JSON_analysieren_2528
    Elemente_abrufen_2752["Elemente_abrufen\n[SharePoint]"]
    JSON_analysieren_2528 --> Elemente_abrufen_2752
    For_each_SP_2976[["For_each_SP"]]
    Elemente_abrufen_2752 --> For_each_SP_2976
    Element_l_schen_3424["Element_löschen\n[SharePoint]"]
    For_each_SP_2976 --> Element_l_schen_3424
    For_each_O365_3200[["For_each_O365"]]
    Element_l_schen_3424 --> For_each_O365_3200
    Benutzerprofil_abrufen_V2_3872["Benutzerprofil_abrufen_(V2)\n[Office 365 Outlook]"]
    For_each_O365_3200 --> Benutzerprofil_abrufen_V2_3872
    Element_erstellen_3648["Element_erstellen\n[SharePoint]"]
    Benutzerprofil_abrufen_V2_3872 --> Element_erstellen_3648
    FLOW_END(["Ende"])
    Element_erstellen_3648 --> FLOW_END

    class TRIGGER trigger
    class HTTP_Anforderung_senden_2304 connector
    class Variable_initialisieren_9168 variable
    class Array_filtern_1856 action
    class JSON_analysieren_2528 data
    class Elemente_abrufen_2752 connector
    class For_each_SP_2976 loop
    class Element_l_schen_3424 connector
    class For_each_O365_3200 loop
    class Benutzerprofil_abrufen_V2_3872 connector
    class Element_erstellen_3648 connector
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


# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ Wenn_ein_Element_erstellt_oder_geändert_wird\n[SharePoint]\n(Recurrence)"])
    nderungen_f_r_ein_Element_oder_eine_Datei_abrufen__8816["Änderungen_für_ein_Element_oder_eine_Datei_abrufen_(nur_Eigenschaften)\n[SharePoint]"]
    TRIGGER --> nderungen_f_r_ein_Element_oder_eine_Datei_abrufen__8816
    Bedingung_7920{{"Bedingung"}}
    nderungen_f_r_ein_Element_oder_eine_Datei_abrufen__8816 --> Bedingung_7920
    Bedingung_Ja_8368(["Bedingung – Ja"])
    Bedingung_7920 -->|Ja| Bedingung_Ja_8368
    Auf_alle_anwenden_8592[["Auf_alle_anwenden"]]
    Bedingung_Ja_8368 --> Auf_alle_anwenden_8592
    Element_Aktualisieren_Setzte_Zeitstempel_9712["Element_Aktualisieren_-_Setzte_Zeitstempel\n[SharePoint]"]
    Auf_alle_anwenden_8592 --> Element_Aktualisieren_Setzte_Zeitstempel_9712
    Auf_alle_anwenden_8144[["Auf_alle_anwenden"]]
    Bedingung_7920 --> Auf_alle_anwenden_8144
    Element_Aktualisieren_Setzte_Zeitstempel_9040["Element_Aktualisieren_-_Setzte_Zeitstempel\n[SharePoint]"]
    Auf_alle_anwenden_8144 --> Element_Aktualisieren_Setzte_Zeitstempel_9040
    Catch_Error_9264(["Catch_Error"])
    Element_Aktualisieren_Setzte_Zeitstempel_9712 --> Catch_Error_9264
    Element_Aktualisieren_Setzte_Zeitstempel_9040 --> Catch_Error_9264
    Parse_JSON_9488["Parse_JSON"]
    Catch_Error_9264 --> Parse_JSON_9488
    FLOW_END(["Ende"])
    Parse_JSON_9488 --> FLOW_END

    class TRIGGER trigger
    class nderungen_f_r_ein_Element_oder_eine_Datei_abrufen__8816 connector
    class Bedingung_7920 condition
    class Bedingung_Ja_8368 branch_true
    class Auf_alle_anwenden_8592 loop
    class Element_Aktualisieren_Setzte_Zeitstempel_9712 connector
    class Auf_alle_anwenden_8144 loop
    class Element_Aktualisieren_Setzte_Zeitstempel_9040 connector
    class Catch_Error_9264 scope
    class Parse_JSON_9488 data
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


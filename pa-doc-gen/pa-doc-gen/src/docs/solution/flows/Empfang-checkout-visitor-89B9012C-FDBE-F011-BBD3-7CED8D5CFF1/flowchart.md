# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ When_a_new_email_arrives_(V3)\n[Office 365 Outlook]\n(OpenApiConnectionNotification)"])
    Bedingung_4320{{"Bedingung"}}
    TRIGGER --> Bedingung_4320
    Bedingung_Ja_4768(["Bedingung – Ja"])
    Bedingung_4320 -->|Ja| Bedingung_Ja_4768
    Elemente_abrufen_5440["Elemente_abrufen\n[SharePoint]"]
    Bedingung_Ja_4768 --> Elemente_abrufen_5440
    Auf_alle_anwenden_5216[["Auf_alle_anwenden"]]
    Elemente_abrufen_5440 --> Auf_alle_anwenden_5216
    Element_aktualisieren_5888["Element_aktualisieren\n[SharePoint]"]
    Auf_alle_anwenden_5216 --> Element_aktualisieren_5888
    Elemente_abrufen_4544["Elemente_abrufen\n[SharePoint]"]
    Bedingung_4320 --> Elemente_abrufen_4544
    Auf_alle_anwenden_4096[["Auf_alle_anwenden"]]
    Elemente_abrufen_4544 --> Auf_alle_anwenden_4096
    Element_aktualisieren_4992["Element_aktualisieren\n[SharePoint]"]
    Auf_alle_anwenden_4096 --> Element_aktualisieren_4992
    FLOW_END(["Ende"])
    Element_aktualisieren_5888 --> FLOW_END
    Element_aktualisieren_4992 --> FLOW_END

    class TRIGGER trigger
    class Bedingung_4320 condition
    class Bedingung_Ja_4768 branch_true
    class Elemente_abrufen_5440 connector
    class Auf_alle_anwenden_5216 loop
    class Element_aktualisieren_5888 connector
    class Elemente_abrufen_4544 connector
    class Auf_alle_anwenden_4096 loop
    class Element_aktualisieren_4992 connector
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


# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ When_a_new_response_is_submitted\n[shared_microsoftforms]\n(OpenApiConnectionWebhook)"])
    Initialize_variable_9840["Initialize_variable"]
    TRIGGER --> Initialize_variable_9840
    Variable_initialisieren_9616["Variable_initialisieren"]
    Initialize_variable_9840 --> Variable_initialisieren_9616
    Antwortdetails_abrufen_64["Antwortdetails_abrufen\n[shared_microsoftforms]"]
    Variable_initialisieren_9616 --> Antwortdetails_abrufen_64
    Absage_288{{"Absage"}}
    Antwortdetails_abrufen_64 --> Absage_288
    Absage_Ja_960(["Absage – Ja"])
    Absage_288 -->|Ja| Absage_Ja_960
    Variable_festlegen_1408["Variable_festlegen"]
    Absage_Ja_960 --> Variable_festlegen_1408
    E_Mail_senden_V2_1184["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Variable_festlegen_1408 --> E_Mail_senden_V2_1184
    Absage_Nein_1632(["Absage – Nein"])
    Absage_288 -->|Nein| Absage_Nein_1632
    E_Mail_senden_V2_2_2080["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Absage_Nein_1632 --> E_Mail_senden_V2_2_2080
    Variable_festlegen_736["Variable_festlegen"]
    Absage_288 --> Variable_festlegen_736
    E_Mail_senden_V2_512["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Variable_festlegen_736 --> E_Mail_senden_V2_512
    FLOW_END(["Ende"])
    E_Mail_senden_V2_1184 --> FLOW_END
    E_Mail_senden_V2_2_2080 --> FLOW_END
    E_Mail_senden_V2_512 --> FLOW_END

    class TRIGGER trigger
    class Initialize_variable_9840 variable
    class Variable_initialisieren_9616 variable
    class Antwortdetails_abrufen_64 connector
    class Absage_288 condition
    class Absage_Ja_960 branch_true
    class Variable_festlegen_1408 variable
    class E_Mail_senden_V2_1184 connector
    class Absage_Nein_1632 branch_false
    class E_Mail_senden_V2_2_2080 connector
    class Variable_festlegen_736 variable
    class E_Mail_senden_V2_512 connector
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


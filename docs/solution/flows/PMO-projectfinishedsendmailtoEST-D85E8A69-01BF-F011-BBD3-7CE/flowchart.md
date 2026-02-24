# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ When_an_item_or_a_file_is_modified\n[SharePoint]\n(Recurrence)"])
    Get_changes_for_an_item_or_a_file_properties_only_1392["Get_changes_for_an_item_or_a_file_(properties_only)\n[SharePoint]"]
    TRIGGER --> Get_changes_for_an_item_or_a_file_properties_only_1392
    Condition_1168{{"Condition"}}
    Get_changes_for_an_item_or_a_file_properties_only_1392 --> Condition_1168
    Condition_Ja_1616(["Condition – Ja"])
    Condition_1168 -->|Ja| Condition_Ja_1616
    Send_an_email_V2_2288["Send_an_email_(V2)\n[Office 365 Outlook]"]
    Condition_Ja_1616 --> Send_an_email_V2_2288
    Send_an_email_V2_1840["Send_an_email_(V2)\n[Office 365 Outlook]"]
    Condition_1168 --> Send_an_email_V2_1840
    FLOW_END(["Ende"])
    Send_an_email_V2_2288 --> FLOW_END
    Send_an_email_V2_1840 --> FLOW_END

    class TRIGGER trigger
    class Get_changes_for_an_item_or_a_file_properties_only_1392 connector
    class Condition_1168 condition
    class Condition_Ja_1616 branch_true
    class Send_an_email_V2_2288 connector
    class Send_an_email_V2_1840 connector
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


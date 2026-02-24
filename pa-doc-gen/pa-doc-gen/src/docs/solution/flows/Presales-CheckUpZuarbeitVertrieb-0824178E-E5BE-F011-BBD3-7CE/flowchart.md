# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ Recurrence\n(Recurrence)"])
    VZeitStempelStatusAbgeschlossen_9616["VZeitStempelStatusAbgeschlossen"]
    TRIGGER --> VZeitStempelStatusAbgeschlossen_9616
    VZeitStempelAngebotErstellt_5856["VZeitStempelAngebotErstellt"]
    VZeitStempelStatusAbgeschlossen_9616 --> VZeitStempelAngebotErstellt_5856
    VEndDatum_2704["VEndDatum"]
    VZeitStempelAngebotErstellt_5856 --> VEndDatum_2704
    VTempCheckIfNull_7936["VTempCheckIfNull"]
    VEndDatum_2704 --> VTempCheckIfNull_7936
    Elemente_abrufen_alle_Presales_Projekte_8544["Elemente_abrufen_alle_Presales_Projekte\n[SharePoint]"]
    VTempCheckIfNull_7936 --> Elemente_abrufen_alle_Presales_Projekte_8544
    Check_Status_Abgeschlossen_3552[["Check_Status_Abgeschlossen"]]
    Elemente_abrufen_alle_Presales_Projekte_8544 --> Check_Status_Abgeschlossen_3552
    Setze_VDatumStatusAbgeschlossen_5824["Setze_VDatumStatusAbgeschlossen"]
    Check_Status_Abgeschlossen_3552 --> Setze_VDatumStatusAbgeschlossen_5824
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__7184{{"Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null"}}
    Setze_VDatumStatusAbgeschlossen_5824 --> Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__7184
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__2656(["Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null – Ja"])
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__7184 -->|Ja| Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__2656
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3328{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__2656 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3328
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6464(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3328 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6464
    Setze_VDatumAngebotErstellt_7360["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6464 --> Setze_VDatumAngebotErstellt_7360
    Variable_festlegen_6912["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_7360 --> Variable_festlegen_6912
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7584{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_6912 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7584
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7808(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7584 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7808
    E_Mail_senden_V2_2_8480["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7808 --> E_Mail_senden_V2_2_8480
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7584 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256
    Auftrag_gewonnen_8928{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256 --> Auftrag_gewonnen_8928
    Auftrag_gewonnen_Ja_9376(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_8928 -->|Ja| Auftrag_gewonnen_Ja_9376
    Auftragsnummer_bekannt_9824{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_9376 --> Auftragsnummer_bekannt_9824
    Auftragsnummer_bekannt_Nein_3344(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_9824 -->|Nein| Auftragsnummer_bekannt_Nein_3344
    E_Mail_senden_V2_3_3792["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_3344 --> E_Mail_senden_V2_3_3792
    Auftragsnummer_bekannt_9152{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_8928 --> Auftragsnummer_bekannt_9152
    Auftragsnummer_bekannt_Nein_8704(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_9152 -->|Nein| Auftragsnummer_bekannt_Nein_8704
    E_Mail_senden_V2_3_9600["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_8704 --> E_Mail_senden_V2_3_9600
    E_Mail_senden_V2_2_8032["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7584 --> E_Mail_senden_V2_2_8032
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3568(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3328 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3568
    Angebot_noch_offen_4240{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3568 --> Angebot_noch_offen_4240
    Angebot_noch_offen_Ja_4016(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_4240 -->|Ja| Angebot_noch_offen_Ja_4016
    E_Mail_senden_V2_4912["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_4016 --> E_Mail_senden_V2_4912
    E_Mail_senden_V2_4464["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_4240 --> E_Mail_senden_V2_4464
    Setze_VDatumAngebotErstellt_3776["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3328 --> Setze_VDatumAngebotErstellt_3776
    Variable_festlegen_3104["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_3776 --> Variable_festlegen_3104
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3552{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_3104 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3552
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4000(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3552 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4000
    E_Mail_senden_V2_2_4672["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4000 --> E_Mail_senden_V2_2_4672
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4448(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3552 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4448
    Auftrag_gewonnen_5120{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4448 --> Auftrag_gewonnen_5120
    Auftrag_gewonnen_Ja_5568(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_5120 -->|Ja| Auftrag_gewonnen_Ja_5568
    Auftragsnummer_bekannt_6240{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_5568 --> Auftragsnummer_bekannt_6240
    Auftragsnummer_bekannt_Nein_6016(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_6240 -->|Nein| Auftragsnummer_bekannt_Nein_6016
    E_Mail_senden_V2_3_6688["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_6016 --> E_Mail_senden_V2_3_6688
    Auftragsnummer_bekannt_5344{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_5120 --> Auftragsnummer_bekannt_5344
    Auftragsnummer_bekannt_Nein_4896(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_5344 -->|Nein| Auftragsnummer_bekannt_Nein_4896
    E_Mail_senden_V2_3_5792["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_4896 --> E_Mail_senden_V2_3_5792
    E_Mail_senden_V2_2_4224["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3552 --> E_Mail_senden_V2_2_4224
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4832{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__7184 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4832
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_7952(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4832 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_7952
    Setze_VDatumAngebotErstellt_8848["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_7952 --> Setze_VDatumAngebotErstellt_8848
    Variable_festlegen_8400["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_8848 --> Variable_festlegen_8400
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8624{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_8400 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8624
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9072(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8624 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9072
    E_Mail_senden_V2_2_9744["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9072 --> E_Mail_senden_V2_2_9744
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9520(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8624 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9520
    Auftrag_gewonnen_192{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9520 --> Auftrag_gewonnen_192
    Auftrag_gewonnen_Ja_640(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_192 -->|Ja| Auftrag_gewonnen_Ja_640
    Auftragsnummer_bekannt_1312{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_640 --> Auftragsnummer_bekannt_1312
    Auftragsnummer_bekannt_Nein_1088(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_1312 -->|Nein| Auftragsnummer_bekannt_Nein_1088
    E_Mail_senden_V2_3_1760["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_1088 --> E_Mail_senden_V2_3_1760
    Auftragsnummer_bekannt_416{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_192 --> Auftragsnummer_bekannt_416
    Auftragsnummer_bekannt_Nein_9968(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_416 -->|Nein| Auftragsnummer_bekannt_Nein_9968
    E_Mail_senden_V2_3_864["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_9968 --> E_Mail_senden_V2_3_864
    E_Mail_senden_V2_2_9296["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8624 --> E_Mail_senden_V2_2_9296
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1536(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4832 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1536
    Angebot_noch_offen_2208{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1536 --> Angebot_noch_offen_2208
    Angebot_noch_offen_Ja_1984(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_2208 -->|Ja| Angebot_noch_offen_Ja_1984
    E_Mail_senden_V2_2880["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_1984 --> E_Mail_senden_V2_2880
    E_Mail_senden_V2_2432["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_2208 --> E_Mail_senden_V2_2432
    Setze_VDatumAngebotErstellt_5088["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4832 --> Setze_VDatumAngebotErstellt_5088
    Variable_festlegen_912["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_5088 --> Variable_festlegen_912
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1152{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_912 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1152
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5936(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1152 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5936
    E_Mail_senden_V2_2_6160["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5936 --> E_Mail_senden_V2_2_6160
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1152 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712
    Auftrag_gewonnen_6608{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712 --> Auftrag_gewonnen_6608
    Auftrag_gewonnen_Ja_7056(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_6608 -->|Ja| Auftrag_gewonnen_Ja_7056
    Auftragsnummer_bekannt_7728{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_7056 --> Auftragsnummer_bekannt_7728
    Auftragsnummer_bekannt_Nein_7504(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_7728 -->|Nein| Auftragsnummer_bekannt_Nein_7504
    E_Mail_senden_V2_3_8176["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_7504 --> E_Mail_senden_V2_3_8176
    Auftragsnummer_bekannt_6832{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_6608 --> Auftragsnummer_bekannt_6832
    Auftragsnummer_bekannt_Nein_6384(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_6832 -->|Nein| Auftragsnummer_bekannt_Nein_6384
    E_Mail_senden_V2_3_7280["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_6384 --> E_Mail_senden_V2_3_7280
    E_Mail_senden_V2_2_5488["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1152 --> E_Mail_senden_V2_2_5488
    FLOW_END(["Ende"])
    E_Mail_senden_V2_2_8480 --> FLOW_END
    E_Mail_senden_V2_3_3792 --> FLOW_END
    E_Mail_senden_V2_3_9600 --> FLOW_END
    E_Mail_senden_V2_2_8032 --> FLOW_END
    E_Mail_senden_V2_4912 --> FLOW_END
    E_Mail_senden_V2_4464 --> FLOW_END
    E_Mail_senden_V2_2_4672 --> FLOW_END
    E_Mail_senden_V2_3_6688 --> FLOW_END
    E_Mail_senden_V2_3_5792 --> FLOW_END
    E_Mail_senden_V2_2_4224 --> FLOW_END
    E_Mail_senden_V2_2_9744 --> FLOW_END
    E_Mail_senden_V2_3_1760 --> FLOW_END
    E_Mail_senden_V2_3_864 --> FLOW_END
    E_Mail_senden_V2_2_9296 --> FLOW_END
    E_Mail_senden_V2_2880 --> FLOW_END
    E_Mail_senden_V2_2432 --> FLOW_END
    E_Mail_senden_V2_2_6160 --> FLOW_END
    E_Mail_senden_V2_3_8176 --> FLOW_END
    E_Mail_senden_V2_3_7280 --> FLOW_END
    E_Mail_senden_V2_2_5488 --> FLOW_END

    class TRIGGER trigger
    class VZeitStempelStatusAbgeschlossen_9616 variable
    class VZeitStempelAngebotErstellt_5856 variable
    class VEndDatum_2704 variable
    class VTempCheckIfNull_7936 variable
    class Elemente_abrufen_alle_Presales_Projekte_8544 connector
    class Check_Status_Abgeschlossen_3552 loop
    class Setze_VDatumStatusAbgeschlossen_5824 variable
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__7184 condition
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__2656 branch_true
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3328 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6464 branch_true
    class Setze_VDatumAngebotErstellt_7360 variable
    class Variable_festlegen_6912 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7584 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7808 branch_true
    class E_Mail_senden_V2_2_8480 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256 branch_false
    class Auftrag_gewonnen_8928 condition
    class Auftrag_gewonnen_Ja_9376 branch_true
    class Auftragsnummer_bekannt_9824 condition
    class Auftragsnummer_bekannt_Nein_3344 branch_false
    class E_Mail_senden_V2_3_3792 connector
    class Auftragsnummer_bekannt_9152 condition
    class Auftragsnummer_bekannt_Nein_8704 branch_false
    class E_Mail_senden_V2_3_9600 connector
    class E_Mail_senden_V2_2_8032 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3568 branch_false
    class Angebot_noch_offen_4240 condition
    class Angebot_noch_offen_Ja_4016 branch_true
    class E_Mail_senden_V2_4912 connector
    class E_Mail_senden_V2_4464 connector
    class Setze_VDatumAngebotErstellt_3776 variable
    class Variable_festlegen_3104 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3552 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4000 branch_true
    class E_Mail_senden_V2_2_4672 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4448 branch_false
    class Auftrag_gewonnen_5120 condition
    class Auftrag_gewonnen_Ja_5568 branch_true
    class Auftragsnummer_bekannt_6240 condition
    class Auftragsnummer_bekannt_Nein_6016 branch_false
    class E_Mail_senden_V2_3_6688 connector
    class Auftragsnummer_bekannt_5344 condition
    class Auftragsnummer_bekannt_Nein_4896 branch_false
    class E_Mail_senden_V2_3_5792 connector
    class E_Mail_senden_V2_2_4224 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4832 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_7952 branch_true
    class Setze_VDatumAngebotErstellt_8848 variable
    class Variable_festlegen_8400 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8624 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9072 branch_true
    class E_Mail_senden_V2_2_9744 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9520 branch_false
    class Auftrag_gewonnen_192 condition
    class Auftrag_gewonnen_Ja_640 branch_true
    class Auftragsnummer_bekannt_1312 condition
    class Auftragsnummer_bekannt_Nein_1088 branch_false
    class E_Mail_senden_V2_3_1760 connector
    class Auftragsnummer_bekannt_416 condition
    class Auftragsnummer_bekannt_Nein_9968 branch_false
    class E_Mail_senden_V2_3_864 connector
    class E_Mail_senden_V2_2_9296 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1536 branch_false
    class Angebot_noch_offen_2208 condition
    class Angebot_noch_offen_Ja_1984 branch_true
    class E_Mail_senden_V2_2880 connector
    class E_Mail_senden_V2_2432 connector
    class Setze_VDatumAngebotErstellt_5088 variable
    class Variable_festlegen_912 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1152 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5936 branch_true
    class E_Mail_senden_V2_2_6160 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712 branch_false
    class Auftrag_gewonnen_6608 condition
    class Auftrag_gewonnen_Ja_7056 branch_true
    class Auftragsnummer_bekannt_7728 condition
    class Auftragsnummer_bekannt_Nein_7504 branch_false
    class E_Mail_senden_V2_3_8176 connector
    class Auftragsnummer_bekannt_6832 condition
    class Auftragsnummer_bekannt_Nein_6384 branch_false
    class E_Mail_senden_V2_3_7280 connector
    class E_Mail_senden_V2_2_5488 connector
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


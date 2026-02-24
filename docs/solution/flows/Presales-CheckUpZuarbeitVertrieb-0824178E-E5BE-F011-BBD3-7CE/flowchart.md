# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ Recurrence\n(Recurrence)"])
    VZeitStempelStatusAbgeschlossen_6880["VZeitStempelStatusAbgeschlossen"]
    TRIGGER --> VZeitStempelStatusAbgeschlossen_6880
    VZeitStempelAngebotErstellt_7232["VZeitStempelAngebotErstellt"]
    VZeitStempelStatusAbgeschlossen_6880 --> VZeitStempelAngebotErstellt_7232
    VEndDatum_8832["VEndDatum"]
    VZeitStempelAngebotErstellt_7232 --> VEndDatum_8832
    VTempCheckIfNull_9120["VTempCheckIfNull"]
    VEndDatum_8832 --> VTempCheckIfNull_9120
    Elemente_abrufen_alle_Presales_Projekte_9728["Elemente_abrufen_alle_Presales_Projekte\n[SharePoint]"]
    VTempCheckIfNull_9120 --> Elemente_abrufen_alle_Presales_Projekte_9728
    Check_Status_Abgeschlossen_864[["Check_Status_Abgeschlossen"]]
    Elemente_abrufen_alle_Presales_Projekte_9728 --> Check_Status_Abgeschlossen_864
    Setze_VDatumStatusAbgeschlossen_7424["Setze_VDatumStatusAbgeschlossen"]
    Check_Status_Abgeschlossen_864 --> Setze_VDatumStatusAbgeschlossen_7424
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8784{{"Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null"}}
    Setze_VDatumStatusAbgeschlossen_7424 --> Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8784
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8896(["Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null – Ja"])
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8784 -->|Ja| Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8896
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_9568{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8896 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_9568
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_2704(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_9568 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_2704
    Setze_VDatumAngebotErstellt_3600["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_2704 --> Setze_VDatumAngebotErstellt_3600
    Variable_festlegen_3152["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_3600 --> Variable_festlegen_3152
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3824{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_3152 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3824
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4048(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3824 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4048
    E_Mail_senden_V2_2_4720["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4048 --> E_Mail_senden_V2_2_4720
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4496(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3824 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4496
    Auftrag_gewonnen_5168{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4496 --> Auftrag_gewonnen_5168
    Auftrag_gewonnen_Ja_5616(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_5168 -->|Ja| Auftrag_gewonnen_Ja_5616
    Auftragsnummer_bekannt_6288{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_5616 --> Auftragsnummer_bekannt_6288
    Auftragsnummer_bekannt_Nein_6064(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_6288 -->|Nein| Auftragsnummer_bekannt_Nein_6064
    E_Mail_senden_V2_3_6608["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_6064 --> E_Mail_senden_V2_3_6608
    Auftragsnummer_bekannt_5392{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_5168 --> Auftragsnummer_bekannt_5392
    Auftragsnummer_bekannt_Nein_4944(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_5392 -->|Nein| Auftragsnummer_bekannt_Nein_4944
    E_Mail_senden_V2_3_5840["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_4944 --> E_Mail_senden_V2_3_5840
    E_Mail_senden_V2_2_4272["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3824 --> E_Mail_senden_V2_2_4272
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6384(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_9568 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6384
    Angebot_noch_offen_7056{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6384 --> Angebot_noch_offen_7056
    Angebot_noch_offen_Ja_6832(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_7056 -->|Ja| Angebot_noch_offen_Ja_6832
    E_Mail_senden_V2_7728["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_6832 --> E_Mail_senden_V2_7728
    E_Mail_senden_V2_7280["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_7056 --> E_Mail_senden_V2_7280
    Setze_VDatumAngebotErstellt_16["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_9568 --> Setze_VDatumAngebotErstellt_16
    Variable_festlegen_9344["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_16 --> Variable_festlegen_9344
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9792{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_9344 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9792
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__240(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9792 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__240
    E_Mail_senden_V2_2_912["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__240 --> E_Mail_senden_V2_2_912
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__688(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9792 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__688
    Auftrag_gewonnen_1360{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__688 --> Auftrag_gewonnen_1360
    Auftrag_gewonnen_Ja_1808(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_1360 -->|Ja| Auftrag_gewonnen_Ja_1808
    Auftragsnummer_bekannt_2480{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_1808 --> Auftragsnummer_bekannt_2480
    Auftragsnummer_bekannt_Nein_2256(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_2480 -->|Nein| Auftragsnummer_bekannt_Nein_2256
    E_Mail_senden_V2_3_2928["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_2256 --> E_Mail_senden_V2_3_2928
    Auftragsnummer_bekannt_1584{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_1360 --> Auftragsnummer_bekannt_1584
    Auftragsnummer_bekannt_Nein_1136(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_1584 -->|Nein| Auftragsnummer_bekannt_Nein_1136
    E_Mail_senden_V2_3_2032["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_1136 --> E_Mail_senden_V2_3_2032
    E_Mail_senden_V2_2_464["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9792 --> E_Mail_senden_V2_2_464
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1072{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8784 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1072
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4192(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1072 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4192
    Setze_VDatumAngebotErstellt_5088["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4192 --> Setze_VDatumAngebotErstellt_5088
    Variable_festlegen_4640["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_5088 --> Variable_festlegen_4640
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4864{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_4640 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4864
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5312(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4864 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5312
    E_Mail_senden_V2_2_5984["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5312 --> E_Mail_senden_V2_2_5984
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5760(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4864 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5760
    Auftrag_gewonnen_6432{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5760 --> Auftrag_gewonnen_6432
    Auftrag_gewonnen_Ja_6880(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_6432 -->|Ja| Auftrag_gewonnen_Ja_6880
    Auftragsnummer_bekannt_7552{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_6880 --> Auftragsnummer_bekannt_7552
    Auftragsnummer_bekannt_Nein_7328(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_7552 -->|Nein| Auftragsnummer_bekannt_Nein_7328
    E_Mail_senden_V2_3_8000["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_7328 --> E_Mail_senden_V2_3_8000
    Auftragsnummer_bekannt_6656{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_6432 --> Auftragsnummer_bekannt_6656
    Auftragsnummer_bekannt_Nein_6208(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_6656 -->|Nein| Auftragsnummer_bekannt_Nein_6208
    E_Mail_senden_V2_3_7104["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_6208 --> E_Mail_senden_V2_3_7104
    E_Mail_senden_V2_2_5536["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4864 --> E_Mail_senden_V2_2_5536
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_7776(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1072 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_7776
    Angebot_noch_offen_8448{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_7776 --> Angebot_noch_offen_8448
    Angebot_noch_offen_Ja_8224(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_8448 -->|Ja| Angebot_noch_offen_Ja_8224
    E_Mail_senden_V2_9120["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_8224 --> E_Mail_senden_V2_9120
    E_Mail_senden_V2_8672["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_8448 --> E_Mail_senden_V2_8672
    Setze_VDatumAngebotErstellt_1328["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1072 --> Setze_VDatumAngebotErstellt_1328
    Variable_festlegen_8016["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_1328 --> Variable_festlegen_8016
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_8016 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2176(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2176
    E_Mail_senden_V2_2_2400["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2176 --> E_Mail_senden_V2_2_2400
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1952(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1952
    Auftrag_gewonnen_2848{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1952 --> Auftrag_gewonnen_2848
    Auftrag_gewonnen_Ja_3296(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_2848 -->|Ja| Auftrag_gewonnen_Ja_3296
    Auftragsnummer_bekannt_3968{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_3296 --> Auftragsnummer_bekannt_3968
    Auftragsnummer_bekannt_Nein_3744(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_3968 -->|Nein| Auftragsnummer_bekannt_Nein_3744
    E_Mail_senden_V2_3_4416["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_3744 --> E_Mail_senden_V2_3_4416
    Auftragsnummer_bekannt_3072{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_2848 --> Auftragsnummer_bekannt_3072
    Auftragsnummer_bekannt_Nein_2624(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_3072 -->|Nein| Auftragsnummer_bekannt_Nein_2624
    E_Mail_senden_V2_3_3520["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_2624 --> E_Mail_senden_V2_3_3520
    E_Mail_senden_V2_2_1728["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256 --> E_Mail_senden_V2_2_1728
    FLOW_END(["Ende"])
    E_Mail_senden_V2_2_4720 --> FLOW_END
    E_Mail_senden_V2_3_6608 --> FLOW_END
    E_Mail_senden_V2_3_5840 --> FLOW_END
    E_Mail_senden_V2_2_4272 --> FLOW_END
    E_Mail_senden_V2_7728 --> FLOW_END
    E_Mail_senden_V2_7280 --> FLOW_END
    E_Mail_senden_V2_2_912 --> FLOW_END
    E_Mail_senden_V2_3_2928 --> FLOW_END
    E_Mail_senden_V2_3_2032 --> FLOW_END
    E_Mail_senden_V2_2_464 --> FLOW_END
    E_Mail_senden_V2_2_5984 --> FLOW_END
    E_Mail_senden_V2_3_8000 --> FLOW_END
    E_Mail_senden_V2_3_7104 --> FLOW_END
    E_Mail_senden_V2_2_5536 --> FLOW_END
    E_Mail_senden_V2_9120 --> FLOW_END
    E_Mail_senden_V2_8672 --> FLOW_END
    E_Mail_senden_V2_2_2400 --> FLOW_END
    E_Mail_senden_V2_3_4416 --> FLOW_END
    E_Mail_senden_V2_3_3520 --> FLOW_END
    E_Mail_senden_V2_2_1728 --> FLOW_END

    class TRIGGER trigger
    class VZeitStempelStatusAbgeschlossen_6880 variable
    class VZeitStempelAngebotErstellt_7232 variable
    class VEndDatum_8832 variable
    class VTempCheckIfNull_9120 variable
    class Elemente_abrufen_alle_Presales_Projekte_9728 connector
    class Check_Status_Abgeschlossen_864 loop
    class Setze_VDatumStatusAbgeschlossen_7424 variable
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8784 condition
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__8896 branch_true
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_9568 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_2704 branch_true
    class Setze_VDatumAngebotErstellt_3600 variable
    class Variable_festlegen_3152 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3824 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4048 branch_true
    class E_Mail_senden_V2_2_4720 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4496 branch_false
    class Auftrag_gewonnen_5168 condition
    class Auftrag_gewonnen_Ja_5616 branch_true
    class Auftragsnummer_bekannt_6288 condition
    class Auftragsnummer_bekannt_Nein_6064 branch_false
    class E_Mail_senden_V2_3_6608 connector
    class Auftragsnummer_bekannt_5392 condition
    class Auftragsnummer_bekannt_Nein_4944 branch_false
    class E_Mail_senden_V2_3_5840 connector
    class E_Mail_senden_V2_2_4272 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6384 branch_false
    class Angebot_noch_offen_7056 condition
    class Angebot_noch_offen_Ja_6832 branch_true
    class E_Mail_senden_V2_7728 connector
    class E_Mail_senden_V2_7280 connector
    class Setze_VDatumAngebotErstellt_16 variable
    class Variable_festlegen_9344 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__9792 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__240 branch_true
    class E_Mail_senden_V2_2_912 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__688 branch_false
    class Auftrag_gewonnen_1360 condition
    class Auftrag_gewonnen_Ja_1808 branch_true
    class Auftragsnummer_bekannt_2480 condition
    class Auftragsnummer_bekannt_Nein_2256 branch_false
    class E_Mail_senden_V2_3_2928 connector
    class Auftragsnummer_bekannt_1584 condition
    class Auftragsnummer_bekannt_Nein_1136 branch_false
    class E_Mail_senden_V2_3_2032 connector
    class E_Mail_senden_V2_2_464 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1072 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4192 branch_true
    class Setze_VDatumAngebotErstellt_5088 variable
    class Variable_festlegen_4640 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4864 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5312 branch_true
    class E_Mail_senden_V2_2_5984 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5760 branch_false
    class Auftrag_gewonnen_6432 condition
    class Auftrag_gewonnen_Ja_6880 branch_true
    class Auftragsnummer_bekannt_7552 condition
    class Auftragsnummer_bekannt_Nein_7328 branch_false
    class E_Mail_senden_V2_3_8000 connector
    class Auftragsnummer_bekannt_6656 condition
    class Auftragsnummer_bekannt_Nein_6208 branch_false
    class E_Mail_senden_V2_3_7104 connector
    class E_Mail_senden_V2_2_5536 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_7776 branch_false
    class Angebot_noch_offen_8448 condition
    class Angebot_noch_offen_Ja_8224 branch_true
    class E_Mail_senden_V2_9120 connector
    class E_Mail_senden_V2_8672 connector
    class Setze_VDatumAngebotErstellt_1328 variable
    class Variable_festlegen_8016 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8256 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2176 branch_true
    class E_Mail_senden_V2_2_2400 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1952 branch_false
    class Auftrag_gewonnen_2848 condition
    class Auftrag_gewonnen_Ja_3296 branch_true
    class Auftragsnummer_bekannt_3968 condition
    class Auftragsnummer_bekannt_Nein_3744 branch_false
    class E_Mail_senden_V2_3_4416 connector
    class Auftragsnummer_bekannt_3072 condition
    class Auftragsnummer_bekannt_Nein_2624 branch_false
    class E_Mail_senden_V2_3_3520 connector
    class E_Mail_senden_V2_2_1728 connector
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


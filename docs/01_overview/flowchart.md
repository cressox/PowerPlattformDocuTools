# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ Recurrence\n(Recurrence)"])
    VZeitStempelStatusAbgeschlossen_5792["VZeitStempelStatusAbgeschlossen"]
    TRIGGER --> VZeitStempelStatusAbgeschlossen_5792
    VZeitStempelAngebotErstellt_5568["VZeitStempelAngebotErstellt"]
    VZeitStempelStatusAbgeschlossen_5792 --> VZeitStempelAngebotErstellt_5568
    VEndDatum_3104["VEndDatum"]
    VZeitStempelAngebotErstellt_5568 --> VEndDatum_3104
    VTempCheckIfNull_7136["VTempCheckIfNull"]
    VEndDatum_3104 --> VTempCheckIfNull_7136
    Elemente_abrufen_alle_Presales_Projekte_6240["Elemente_abrufen_alle_Presales_Projekte\n[SharePoint]"]
    VTempCheckIfNull_7136 --> Elemente_abrufen_alle_Presales_Projekte_6240
    Check_Status_Abgeschlossen_6688[["Check_Status_Abgeschlossen"]]
    Elemente_abrufen_alle_Presales_Projekte_6240 --> Check_Status_Abgeschlossen_6688
    Setze_VDatumStatusAbgeschlossen_6016["Setze_VDatumStatusAbgeschlossen"]
    Check_Status_Abgeschlossen_6688 --> Setze_VDatumStatusAbgeschlossen_6016
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3776{{"Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null"}}
    Setze_VDatumStatusAbgeschlossen_6016 --> Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3776
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__1232(["Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null – Ja"])
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3776 -->|Ja| Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__1232
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1904{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__1232 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1904
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_5040(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1904 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_5040
    Setze_VDatumAngebotErstellt_5936["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_5040 --> Setze_VDatumAngebotErstellt_5936
    Variable_festlegen_5488["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_5936 --> Variable_festlegen_5488
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_5488 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6160(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6160
    E_Mail_senden_V2_2_6832["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6160 --> E_Mail_senden_V2_2_6832
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6608(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6608
    Auftrag_gewonnen_7280{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6608 --> Auftrag_gewonnen_7280
    Auftrag_gewonnen_Ja_7728(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_7280 -->|Ja| Auftrag_gewonnen_Ja_7728
    Auftragsnummer_bekannt_8400{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_7728 --> Auftragsnummer_bekannt_8400
    Auftragsnummer_bekannt_Nein_8176(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_8400 -->|Nein| Auftragsnummer_bekannt_Nein_8176
    E_Mail_senden_V2_3_8848["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_8176 --> E_Mail_senden_V2_3_8848
    Auftragsnummer_bekannt_7504{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_7280 --> Auftragsnummer_bekannt_7504
    Auftragsnummer_bekannt_Nein_7056(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_7504 -->|Nein| Auftragsnummer_bekannt_Nein_7056
    E_Mail_senden_V2_3_7952["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_7056 --> E_Mail_senden_V2_3_7952
    E_Mail_senden_V2_2_6384["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712 --> E_Mail_senden_V2_2_6384
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_8624(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1904 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_8624
    Angebot_noch_offen_9296{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_8624 --> Angebot_noch_offen_9296
    Angebot_noch_offen_Ja_9072(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_9296 -->|Ja| Angebot_noch_offen_Ja_9072
    E_Mail_senden_V2_9968["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_9072 --> E_Mail_senden_V2_9968
    E_Mail_senden_V2_9520["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_9296 --> E_Mail_senden_V2_9520
    Setze_VDatumAngebotErstellt_2352["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1904 --> Setze_VDatumAngebotErstellt_2352
    Variable_festlegen_1680["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_2352 --> Variable_festlegen_1680
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2128{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_1680 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2128
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2576(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2128 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2576
    E_Mail_senden_V2_2_3248["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2576 --> E_Mail_senden_V2_2_3248
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3024(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2128 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3024
    Auftrag_gewonnen_3696{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3024 --> Auftrag_gewonnen_3696
    Auftrag_gewonnen_Ja_4144(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_3696 -->|Ja| Auftrag_gewonnen_Ja_4144
    Auftragsnummer_bekannt_4816{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_4144 --> Auftragsnummer_bekannt_4816
    Auftragsnummer_bekannt_Nein_4592(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_4816 -->|Nein| Auftragsnummer_bekannt_Nein_4592
    E_Mail_senden_V2_3_5264["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_4592 --> E_Mail_senden_V2_3_5264
    Auftragsnummer_bekannt_3920{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_3696 --> Auftragsnummer_bekannt_3920
    Auftragsnummer_bekannt_Nein_3472(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_3920 -->|Nein| Auftragsnummer_bekannt_Nein_3472
    E_Mail_senden_V2_3_4368["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_3472 --> E_Mail_senden_V2_3_4368
    E_Mail_senden_V2_2_2800["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2128 --> E_Mail_senden_V2_2_2800
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4224{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3776 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4224
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6528(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4224 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6528
    Setze_VDatumAngebotErstellt_7424["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6528 --> Setze_VDatumAngebotErstellt_7424
    Variable_festlegen_6976["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_7424 --> Variable_festlegen_6976
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7200{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_6976 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7200
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7648(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7200 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7648
    E_Mail_senden_V2_2_8320["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7648 --> E_Mail_senden_V2_2_8320
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8096(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7200 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8096
    Auftrag_gewonnen_8768{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8096 --> Auftrag_gewonnen_8768
    Auftrag_gewonnen_Ja_9216(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_8768 -->|Ja| Auftrag_gewonnen_Ja_9216
    Auftragsnummer_bekannt_9888{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_9216 --> Auftragsnummer_bekannt_9888
    Auftragsnummer_bekannt_Nein_9664(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_9888 -->|Nein| Auftragsnummer_bekannt_Nein_9664
    E_Mail_senden_V2_3_336["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_9664 --> E_Mail_senden_V2_3_336
    Auftragsnummer_bekannt_8992{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_8768 --> Auftragsnummer_bekannt_8992
    Auftragsnummer_bekannt_Nein_8544(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_8992 -->|Nein| Auftragsnummer_bekannt_Nein_8544
    E_Mail_senden_V2_3_9440["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_8544 --> E_Mail_senden_V2_3_9440
    E_Mail_senden_V2_2_7872["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7200 --> E_Mail_senden_V2_2_7872
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_112(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4224 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_112
    Angebot_noch_offen_784{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_112 --> Angebot_noch_offen_784
    Angebot_noch_offen_Ja_560(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_784 -->|Ja| Angebot_noch_offen_Ja_560
    E_Mail_senden_V2_1456["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_560 --> E_Mail_senden_V2_1456
    E_Mail_senden_V2_1008["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_784 --> E_Mail_senden_V2_1008
    Setze_VDatumAngebotErstellt_6912["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4224 --> Setze_VDatumAngebotErstellt_6912
    Variable_festlegen_3328["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_6912 --> Variable_festlegen_3328
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4672{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_3328 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4672
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6464(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4672 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6464
    E_Mail_senden_V2_2_5344["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6464 --> E_Mail_senden_V2_2_5344
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2656(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4672 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2656
    Auftrag_gewonnen_3376{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2656 --> Auftrag_gewonnen_3376
    Auftrag_gewonnen_Ja_5632(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_3376 -->|Ja| Auftrag_gewonnen_Ja_5632
    Auftragsnummer_bekannt_6304{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_5632 --> Auftragsnummer_bekannt_6304
    Auftragsnummer_bekannt_Nein_6080(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_6304 -->|Nein| Auftragsnummer_bekannt_Nein_6080
    E_Mail_senden_V2_3_6752["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_6080 --> E_Mail_senden_V2_3_6752
    Auftragsnummer_bekannt_2432{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_3376 --> Auftragsnummer_bekannt_2432
    Auftragsnummer_bekannt_Nein_5408(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_2432 -->|Nein| Auftragsnummer_bekannt_Nein_5408
    E_Mail_senden_V2_3_5856["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_5408 --> E_Mail_senden_V2_3_5856
    E_Mail_senden_V2_2_5120["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4672 --> E_Mail_senden_V2_2_5120
    FLOW_END(["Ende"])
    E_Mail_senden_V2_2_6832 --> FLOW_END
    E_Mail_senden_V2_3_8848 --> FLOW_END
    E_Mail_senden_V2_3_7952 --> FLOW_END
    E_Mail_senden_V2_2_6384 --> FLOW_END
    E_Mail_senden_V2_9968 --> FLOW_END
    E_Mail_senden_V2_9520 --> FLOW_END
    E_Mail_senden_V2_2_3248 --> FLOW_END
    E_Mail_senden_V2_3_5264 --> FLOW_END
    E_Mail_senden_V2_3_4368 --> FLOW_END
    E_Mail_senden_V2_2_2800 --> FLOW_END
    E_Mail_senden_V2_2_8320 --> FLOW_END
    E_Mail_senden_V2_3_336 --> FLOW_END
    E_Mail_senden_V2_3_9440 --> FLOW_END
    E_Mail_senden_V2_2_7872 --> FLOW_END
    E_Mail_senden_V2_1456 --> FLOW_END
    E_Mail_senden_V2_1008 --> FLOW_END
    E_Mail_senden_V2_2_5344 --> FLOW_END
    E_Mail_senden_V2_3_6752 --> FLOW_END
    E_Mail_senden_V2_3_5856 --> FLOW_END
    E_Mail_senden_V2_2_5120 --> FLOW_END

    class TRIGGER trigger
    class VZeitStempelStatusAbgeschlossen_5792 variable
    class VZeitStempelAngebotErstellt_5568 variable
    class VEndDatum_3104 variable
    class VTempCheckIfNull_7136 variable
    class Elemente_abrufen_alle_Presales_Projekte_6240 connector
    class Check_Status_Abgeschlossen_6688 loop
    class Setze_VDatumStatusAbgeschlossen_6016 variable
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3776 condition
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__1232 branch_true
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1904 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_5040 branch_true
    class Setze_VDatumAngebotErstellt_5936 variable
    class Variable_festlegen_5488 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5712 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6160 branch_true
    class E_Mail_senden_V2_2_6832 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6608 branch_false
    class Auftrag_gewonnen_7280 condition
    class Auftrag_gewonnen_Ja_7728 branch_true
    class Auftragsnummer_bekannt_8400 condition
    class Auftragsnummer_bekannt_Nein_8176 branch_false
    class E_Mail_senden_V2_3_8848 connector
    class Auftragsnummer_bekannt_7504 condition
    class Auftragsnummer_bekannt_Nein_7056 branch_false
    class E_Mail_senden_V2_3_7952 connector
    class E_Mail_senden_V2_2_6384 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_8624 branch_false
    class Angebot_noch_offen_9296 condition
    class Angebot_noch_offen_Ja_9072 branch_true
    class E_Mail_senden_V2_9968 connector
    class E_Mail_senden_V2_9520 connector
    class Setze_VDatumAngebotErstellt_2352 variable
    class Variable_festlegen_1680 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2128 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2576 branch_true
    class E_Mail_senden_V2_2_3248 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3024 branch_false
    class Auftrag_gewonnen_3696 condition
    class Auftrag_gewonnen_Ja_4144 branch_true
    class Auftragsnummer_bekannt_4816 condition
    class Auftragsnummer_bekannt_Nein_4592 branch_false
    class E_Mail_senden_V2_3_5264 connector
    class Auftragsnummer_bekannt_3920 condition
    class Auftragsnummer_bekannt_Nein_3472 branch_false
    class E_Mail_senden_V2_3_4368 connector
    class E_Mail_senden_V2_2_2800 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4224 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6528 branch_true
    class Setze_VDatumAngebotErstellt_7424 variable
    class Variable_festlegen_6976 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7200 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7648 branch_true
    class E_Mail_senden_V2_2_8320 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8096 branch_false
    class Auftrag_gewonnen_8768 condition
    class Auftrag_gewonnen_Ja_9216 branch_true
    class Auftragsnummer_bekannt_9888 condition
    class Auftragsnummer_bekannt_Nein_9664 branch_false
    class E_Mail_senden_V2_3_336 connector
    class Auftragsnummer_bekannt_8992 condition
    class Auftragsnummer_bekannt_Nein_8544 branch_false
    class E_Mail_senden_V2_3_9440 connector
    class E_Mail_senden_V2_2_7872 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_112 branch_false
    class Angebot_noch_offen_784 condition
    class Angebot_noch_offen_Ja_560 branch_true
    class E_Mail_senden_V2_1456 connector
    class E_Mail_senden_V2_1008 connector
    class Setze_VDatumAngebotErstellt_6912 variable
    class Variable_festlegen_3328 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4672 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6464 branch_true
    class E_Mail_senden_V2_2_5344 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2656 branch_false
    class Auftrag_gewonnen_3376 condition
    class Auftrag_gewonnen_Ja_5632 branch_true
    class Auftragsnummer_bekannt_6304 condition
    class Auftragsnummer_bekannt_Nein_6080 branch_false
    class E_Mail_senden_V2_3_6752 connector
    class Auftragsnummer_bekannt_2432 condition
    class Auftragsnummer_bekannt_Nein_5408 branch_false
    class E_Mail_senden_V2_3_5856 connector
    class E_Mail_senden_V2_2_5120 connector
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


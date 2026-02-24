# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ Recurrence\n(Recurrence)"])
    VZeitStempelStatusAbgeschlossen_2400["VZeitStempelStatusAbgeschlossen"]
    TRIGGER --> VZeitStempelStatusAbgeschlossen_2400
    VZeitStempelAngebotErstellt_2176["VZeitStempelAngebotErstellt"]
    VZeitStempelStatusAbgeschlossen_2400 --> VZeitStempelAngebotErstellt_2176
    VEndDatum_2624["VEndDatum"]
    VZeitStempelAngebotErstellt_2176 --> VEndDatum_2624
    VTempCheckIfNull_3072["VTempCheckIfNull"]
    VEndDatum_2624 --> VTempCheckIfNull_3072
    Elemente_abrufen_alle_Presales_Projekte_2848["Elemente_abrufen_alle_Presales_Projekte\n[SharePoint]"]
    VTempCheckIfNull_3072 --> Elemente_abrufen_alle_Presales_Projekte_2848
    Check_Status_Abgeschlossen_3296[["Check_Status_Abgeschlossen"]]
    Elemente_abrufen_alle_Presales_Projekte_2848 --> Check_Status_Abgeschlossen_3296
    Setze_VDatumStatusAbgeschlossen_3744["Setze_VDatumStatusAbgeschlossen"]
    Check_Status_Abgeschlossen_3296 --> Setze_VDatumStatusAbgeschlossen_3744
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3520{{"Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null"}}
    Setze_VDatumStatusAbgeschlossen_3744 --> Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3520
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__2672(["Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null – Ja"])
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3520 -->|Ja| Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__2672
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3344{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__2672 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3344
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6480(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3344 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6480
    Setze_VDatumAngebotErstellt_7376["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6480 --> Setze_VDatumAngebotErstellt_7376
    Variable_festlegen_6928["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_7376 --> Variable_festlegen_6928
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7152{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_6928 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7152
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7600(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7152 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7600
    E_Mail_senden_V2_2_8272["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7600 --> E_Mail_senden_V2_2_8272
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8048(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7152 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8048
    Auftrag_gewonnen_8720{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8048 --> Auftrag_gewonnen_8720
    Auftrag_gewonnen_Ja_9168(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_8720 -->|Ja| Auftrag_gewonnen_Ja_9168
    Auftragsnummer_bekannt_9840{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_9168 --> Auftragsnummer_bekannt_9840
    Auftragsnummer_bekannt_Nein_9616(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_9840 -->|Nein| Auftragsnummer_bekannt_Nein_9616
    E_Mail_senden_V2_3_288["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_9616 --> E_Mail_senden_V2_3_288
    Auftragsnummer_bekannt_8944{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_8720 --> Auftragsnummer_bekannt_8944
    Auftragsnummer_bekannt_Nein_8496(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_8944 -->|Nein| Auftragsnummer_bekannt_Nein_8496
    E_Mail_senden_V2_3_9392["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_8496 --> E_Mail_senden_V2_3_9392
    E_Mail_senden_V2_2_7824["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7152 --> E_Mail_senden_V2_2_7824
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_64(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3344 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_64
    Angebot_noch_offen_736{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_64 --> Angebot_noch_offen_736
    Angebot_noch_offen_Ja_512(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_736 -->|Ja| Angebot_noch_offen_Ja_512
    E_Mail_senden_V2_1408["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_512 --> E_Mail_senden_V2_1408
    E_Mail_senden_V2_960["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_736 --> E_Mail_senden_V2_960
    Setze_VDatumAngebotErstellt_3792["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3344 --> Setze_VDatumAngebotErstellt_3792
    Variable_festlegen_3120["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_3792 --> Variable_festlegen_3120
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3568{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_3120 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3568
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4016(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3568 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4016
    E_Mail_senden_V2_2_4688["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4016 --> E_Mail_senden_V2_2_4688
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4464(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3568 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4464
    Auftrag_gewonnen_5136{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4464 --> Auftrag_gewonnen_5136
    Auftrag_gewonnen_Ja_5584(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_5136 -->|Ja| Auftrag_gewonnen_Ja_5584
    Auftragsnummer_bekannt_6256{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_5584 --> Auftragsnummer_bekannt_6256
    Auftragsnummer_bekannt_Nein_6032(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_6256 -->|Nein| Auftragsnummer_bekannt_Nein_6032
    E_Mail_senden_V2_3_6704["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_6032 --> E_Mail_senden_V2_3_6704
    Auftragsnummer_bekannt_5360{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_5136 --> Auftragsnummer_bekannt_5360
    Auftragsnummer_bekannt_Nein_4912(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_5360 -->|Nein| Auftragsnummer_bekannt_Nein_4912
    E_Mail_senden_V2_3_5808["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_4912 --> E_Mail_senden_V2_3_5808
    E_Mail_senden_V2_2_4240["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3568 --> E_Mail_senden_V2_2_4240
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4416{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3520 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4416
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6560(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4416 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6560
    Setze_VDatumAngebotErstellt_4544["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6560 --> Setze_VDatumAngebotErstellt_4544
    Variable_festlegen_3296["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_4544 --> Variable_festlegen_3296
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2848{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_3296 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2848
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3520(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2848 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3520
    E_Mail_senden_V2_2_4192["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3520 --> E_Mail_senden_V2_2_4192
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3968(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2848 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3968
    Auftrag_gewonnen_4640{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3968 --> Auftrag_gewonnen_4640
    Auftrag_gewonnen_Ja_656(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_4640 -->|Ja| Auftrag_gewonnen_Ja_656
    Auftragsnummer_bekannt_1328{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_656 --> Auftragsnummer_bekannt_1328
    Auftragsnummer_bekannt_Nein_1104(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_1328 -->|Nein| Auftragsnummer_bekannt_Nein_1104
    E_Mail_senden_V2_3_1776["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_1104 --> E_Mail_senden_V2_3_1776
    Auftragsnummer_bekannt_4416{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_4640 --> Auftragsnummer_bekannt_4416
    Auftragsnummer_bekannt_Nein_432(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_4416 -->|Nein| Auftragsnummer_bekannt_Nein_432
    E_Mail_senden_V2_3_880["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_432 --> E_Mail_senden_V2_3_880
    E_Mail_senden_V2_2_3744["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2848 --> E_Mail_senden_V2_2_3744
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1552(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4416 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1552
    Angebot_noch_offen_2224{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1552 --> Angebot_noch_offen_2224
    Angebot_noch_offen_Ja_2000(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_2224 -->|Ja| Angebot_noch_offen_Ja_2000
    E_Mail_senden_V2_2896["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_2000 --> E_Mail_senden_V2_2896
    E_Mail_senden_V2_2448["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_2224 --> E_Mail_senden_V2_2448
    Setze_VDatumAngebotErstellt_3968["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4416 --> Setze_VDatumAngebotErstellt_3968
    Variable_festlegen_4192["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_3968 --> Variable_festlegen_4192
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3424{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_4192 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3424
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3200(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3424 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3200
    E_Mail_senden_V2_2_4320["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3200 --> E_Mail_senden_V2_2_4320
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3648(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3424 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3648
    Auftrag_gewonnen_5216{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3648 --> Auftrag_gewonnen_5216
    Auftrag_gewonnen_Ja_5664(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_5216 -->|Ja| Auftrag_gewonnen_Ja_5664
    Auftragsnummer_bekannt_5888{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_5664 --> Auftragsnummer_bekannt_5888
    Auftragsnummer_bekannt_Nein_6112(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_5888 -->|Nein| Auftragsnummer_bekannt_Nein_6112
    E_Mail_senden_V2_3_4768["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_6112 --> E_Mail_senden_V2_3_4768
    Auftragsnummer_bekannt_4992{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_5216 --> Auftragsnummer_bekannt_4992
    Auftragsnummer_bekannt_Nein_4096(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_4992 -->|Nein| Auftragsnummer_bekannt_Nein_4096
    E_Mail_senden_V2_3_5440["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_4096 --> E_Mail_senden_V2_3_5440
    E_Mail_senden_V2_2_3872["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3424 --> E_Mail_senden_V2_2_3872
    Catch_Error_1184(["Catch_Error"])
    E_Mail_senden_V2_2_8272 --> Catch_Error_1184
    E_Mail_senden_V2_3_288 --> Catch_Error_1184
    E_Mail_senden_V2_3_9392 --> Catch_Error_1184
    E_Mail_senden_V2_2_7824 --> Catch_Error_1184
    E_Mail_senden_V2_1408 --> Catch_Error_1184
    E_Mail_senden_V2_960 --> Catch_Error_1184
    E_Mail_senden_V2_2_4688 --> Catch_Error_1184
    E_Mail_senden_V2_3_6704 --> Catch_Error_1184
    E_Mail_senden_V2_3_5808 --> Catch_Error_1184
    E_Mail_senden_V2_2_4240 --> Catch_Error_1184
    E_Mail_senden_V2_2_4192 --> Catch_Error_1184
    E_Mail_senden_V2_3_1776 --> Catch_Error_1184
    E_Mail_senden_V2_3_880 --> Catch_Error_1184
    E_Mail_senden_V2_2_3744 --> Catch_Error_1184
    E_Mail_senden_V2_2896 --> Catch_Error_1184
    E_Mail_senden_V2_2448 --> Catch_Error_1184
    E_Mail_senden_V2_2_4320 --> Catch_Error_1184
    E_Mail_senden_V2_3_4768 --> Catch_Error_1184
    E_Mail_senden_V2_3_5440 --> Catch_Error_1184
    E_Mail_senden_V2_2_3872 --> Catch_Error_1184
    Parse_JSON_1856["Parse_JSON"]
    Catch_Error_1184 --> Parse_JSON_1856
    FLOW_END(["Ende"])
    Parse_JSON_1856 --> FLOW_END

    class TRIGGER trigger
    class VZeitStempelStatusAbgeschlossen_2400 variable
    class VZeitStempelAngebotErstellt_2176 variable
    class VEndDatum_2624 variable
    class VTempCheckIfNull_3072 variable
    class Elemente_abrufen_alle_Presales_Projekte_2848 connector
    class Check_Status_Abgeschlossen_3296 loop
    class Setze_VDatumStatusAbgeschlossen_3744 variable
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__3520 condition
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__2672 branch_true
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3344 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6480 branch_true
    class Setze_VDatumAngebotErstellt_7376 variable
    class Variable_festlegen_6928 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7152 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__7600 branch_true
    class E_Mail_senden_V2_2_8272 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__8048 branch_false
    class Auftrag_gewonnen_8720 condition
    class Auftrag_gewonnen_Ja_9168 branch_true
    class Auftragsnummer_bekannt_9840 condition
    class Auftragsnummer_bekannt_Nein_9616 branch_false
    class E_Mail_senden_V2_3_288 connector
    class Auftragsnummer_bekannt_8944 condition
    class Auftragsnummer_bekannt_Nein_8496 branch_false
    class E_Mail_senden_V2_3_9392 connector
    class E_Mail_senden_V2_2_7824 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_64 branch_false
    class Angebot_noch_offen_736 condition
    class Angebot_noch_offen_Ja_512 branch_true
    class E_Mail_senden_V2_1408 connector
    class E_Mail_senden_V2_960 connector
    class Setze_VDatumAngebotErstellt_3792 variable
    class Variable_festlegen_3120 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3568 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4016 branch_true
    class E_Mail_senden_V2_2_4688 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4464 branch_false
    class Auftrag_gewonnen_5136 condition
    class Auftrag_gewonnen_Ja_5584 branch_true
    class Auftragsnummer_bekannt_6256 condition
    class Auftragsnummer_bekannt_Nein_6032 branch_false
    class E_Mail_senden_V2_3_6704 connector
    class Auftragsnummer_bekannt_5360 condition
    class Auftragsnummer_bekannt_Nein_4912 branch_false
    class E_Mail_senden_V2_3_5808 connector
    class E_Mail_senden_V2_2_4240 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4416 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6560 branch_true
    class Setze_VDatumAngebotErstellt_4544 variable
    class Variable_festlegen_3296 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2848 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3520 branch_true
    class E_Mail_senden_V2_2_4192 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3968 branch_false
    class Auftrag_gewonnen_4640 condition
    class Auftrag_gewonnen_Ja_656 branch_true
    class Auftragsnummer_bekannt_1328 condition
    class Auftragsnummer_bekannt_Nein_1104 branch_false
    class E_Mail_senden_V2_3_1776 connector
    class Auftragsnummer_bekannt_4416 condition
    class Auftragsnummer_bekannt_Nein_432 branch_false
    class E_Mail_senden_V2_3_880 connector
    class E_Mail_senden_V2_2_3744 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_1552 branch_false
    class Angebot_noch_offen_2224 condition
    class Angebot_noch_offen_Ja_2000 branch_true
    class E_Mail_senden_V2_2896 connector
    class E_Mail_senden_V2_2448 connector
    class Setze_VDatumAngebotErstellt_3968 variable
    class Variable_festlegen_4192 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3424 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3200 branch_true
    class E_Mail_senden_V2_2_4320 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__3648 branch_false
    class Auftrag_gewonnen_5216 condition
    class Auftrag_gewonnen_Ja_5664 branch_true
    class Auftragsnummer_bekannt_5888 condition
    class Auftragsnummer_bekannt_Nein_6112 branch_false
    class E_Mail_senden_V2_3_4768 connector
    class Auftragsnummer_bekannt_4992 condition
    class Auftragsnummer_bekannt_Nein_4096 branch_false
    class E_Mail_senden_V2_3_5440 connector
    class E_Mail_senden_V2_2_3872 connector
    class Catch_Error_1184 scope
    class Parse_JSON_1856 data
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


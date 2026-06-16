# PSN_TRX 部品表（BOM）

50MHz 帯 PSN 方式 SSB トランシーバ。
スケマティック (`PSN_TRX.kicad_sch`) から自動生成。

機械可読版は [`bom.csv`](bom.csv)。

---

## 抵抗 R

| Reference | Value | Footprint | Qty |
|---|---|---|---|
| R1 | 120 | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 1 |
| R15, R44, R41, R34 | 100 | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 4 |
| R2 | 1M | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 1 |
| R21 | 220k | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 1 |
| R25, R29, R43 | 330 | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 3 |
| R26, R12, R16, R27, R11 | 10k | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 5 |
| R3 | 4.7 | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 1 |
| R31, R17, R6, R28, R42, R23, R8, R20 | 100k | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 8 |
| R32, R24, R13, R30, R33, R18, R7, R5, R40, R9, R10, R22 | 1k | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 12 |
| R35, R14 | 20k | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 2 |
| R38 | 4.7k | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 1 |
| R4 | 1.5k | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 1 |
| R52, R36, R51 | 51 | Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical | 3 |

## コンデンサ C

| Reference | Value | Footprint | Qty |
|---|---|---|---|
| C11, C14, C12 | 47p | Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm | 3 |
| C119, C113, C124, C115, C118, C104, C112, C117, C105, C100, C126, C122, C102, C114, C120, C121, C103, C116, C111, C125, C123, C101 | 0.01u | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm | 22 |
| C163, C165, C162, C159, C164, C158, C160, C166, C167, C161 | 1u | Capacitor_THT:CP_Radial_D5.0mm_P2.00mm | 10 |
| C20, C29, C3 | 0.001u | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm | 3 |
| C25, C19 | 33p | Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm | 2 |
| C28, C30 | 100u | Capacitor_THT:CP_Radial_D6.3mm_P2.50mm | 2 |
| C31, C23, C18, C17, C1, C24, C2 | 15p | Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm | 7 |
| C32, C13 | 5p | Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm | 2 |
| C4, C6, C7 | 0.1u | Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm | 3 |
| C5, C8, C8b1 | 10u | Capacitor_THT:CP_Radial_D5.0mm_P2.00mm | 3 |
| C9, C10 | 100p | Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm | 2 |

## コイル L

| Reference | Value | Footprint | Qty |
|---|---|---|---|
| L1, L7, L6, L12, L11, L2, L3, L13 | 7T50 | PSN_TRX:L_FCZ07S_CT | 8 |
| L10, L9 | 1mH | PSN_TRX:L_AL0510-153K_Vertical | 2 |
| L14, L15 | T-50-10 18T/0.4mm | PSN_TRX:L_T50_2pin_Vertical | 2 |
| L4 | T-30-10 6T/0.4mm | PSN_TRX:L_T30_2pin_Vertical | 1 |
| L5 | T-30-10 6T+1T/0.4mm | PSN_TRX:L_T30_3pin_Vertical | 1 |
| L8 | 15mH | PSN_TRX:L_AL0510-153K_Vertical | 1 |
| LED1 | LED | Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical | 1 |
| LED2 | LED黄 | Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical | 1 |

## ダイオード D

| Reference | Value | Footprint | Qty |
|---|---|---|---|
| D8, D1, D7, D3, D2, D4 | 1N60 | Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_CathodeUp | 6 |

## トランス T

| Reference | Value | Footprint | Qty |
|---|---|---|---|
| T1 | ST-71 | PSN_TRX:Transformer_ST71_CB19 | 1 |
| TC2, TC1 | 40p | PSN_TRX:C_Trimmer_TMCV01 | 2 |
| TC3 | 30p | PSN_TRX:C_Trimmer_TMCV01 | 1 |

## トランジスタ Q

| Reference | Value | Footprint | Qty |
|---|---|---|---|
| Q1 | 3SK59 | Package_TO_SOT_THT:TO-72-4 | 1 |
| Q12, Q17, Q11, Q13, Q4, Q15, Q3 | 2SC1815 | Package_TO_SOT_THT:TO-92_Inline | 7 |
| Q14, Q10, Q9 | 2SK439 | Package_TO_SOT_THT:TO-92_Inline | 3 |
| Q5 | 2SC2120 | Package_TO_SOT_THT:TO-92_Inline | 1 |
| Q6 | 2SA950 | Package_TO_SOT_THT:TO-92_Inline | 1 |
| Q8, Q2, Q7 | 2SC1923 | Package_TO_SOT_THT:TO-92_Inline | 3 |

## 水晶振動子

| Reference | Value | Footprint | Qty |
|---|---|---|---|
| X1 | 50.5MHz/3 | Crystal:Crystal_HC49-4H_Vertical | 1 |


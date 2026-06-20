# PSN_TRX 部品表（BOM）

50MHz 帯 PSN 方式 SSB トランシーバ。  
スケマティック (`PSN_TRX.kicad_sch`) から生成・手動補完。

機械可読版は [`bom.csv`](bom.csv)。

> **最終更新: 2026-06-17**
> - Q8: 2SC1971 → **RD06HVF1**（RF N-ch MOSFET）に換装
> - Q3: 3SK59 (TO-72 THT) → **BF998 (SOT-143 SMD)**（デュアルゲート MOSFET）に換装
> - D3, D4: 削除（VR3 pin3 を GND へ直結配線）
> - R20: 10Ω → **0R**（ソース直結 GND）

---

## 抵抗 R（固定）

| Reference | 値 | フットプリント | 数量 |
|---|---|---|---|
| R1 | 120Ω | R_Axial_DIN0207 縦 | 1 |
| R3 | 4.7Ω | R_Axial_DIN0207 縦 | 1 |
| R4 | 1.5kΩ | R_Axial_DIN0207 縦 | 1 |
| R15, R34, R41, R44 | 100Ω | R_Axial_DIN0207 縦 | 4 |
| R17, R6, R8, R20, R23, R42 | 100kΩ | R_Axial_DIN0207 縦 | 6 |
| R21 | 220kΩ | R_Axial_DIN0207 縦 | 1 |
| R5, R7, R9, R10, R13, R18, R22, R24, R33, R40 | 1kΩ | R_Axial_DIN0207 縦 | 10 |
| R25, R30, R43 | 330Ω | R_Axial_DIN0207 縦 | 3 |
| R11, R12, R16, R26, R27 | 10kΩ | R_Axial_DIN0207 縦 | 5 |
| R2, R28, R31 | 1MΩ | R_Axial_DIN0207 縦 | 3 |
| R14, R35 | 20kΩ | R_Axial_DIN0207 縦 | 2 |
| R36, R39, R51 | 51Ω | R_Axial_DIN0207 縦 | 3 |
| R29, R32, R38 | 4.7kΩ | R_Axial_DIN0207 縦 | 3 |

**固定抵抗 合計: 43本**

---

## 抵抗 R（1W PA バイアス回路）

| Reference | 値 | フットプリント | 備考 |
|---|---|---|---|
| R22（PA） | 470Ω | R_Axial_DIN0207 横 P10.16mm | ゲートバイアス上側分圧 |
| R21（PA） | 10Ω | R_Axial_DIN0207 横 P10.16mm | ゲートストッパー |
| R20（PA） | **0R（ジャンパ）** | R_Axial_DIN0207 横 P10.16mm | ソース直結 GND（ジャンパ線で代替可） |

---

## 可変抵抗 VR

| Reference | 値 | フットプリント | 数量 | 備考 |
|---|---|---|---|---|
| VR1 | 5kΩ | PinHeader_1x03 P2.54mm（外付け） | 1 | |
| VR2 | 10kΩ | PinHeader_1x03 P2.54mm（外付け） | 1 | |
| VR3 | 500Ω | Potentiometer_Bourns_3266W_Vertical | 1 | Idq 調整用トリマポット（50〜80mA に設定） |
| VR4, VR5 | 1kΩ | Potentiometer_Alps_RK09K_Single_Vertical | 2 | |

---

## コンデンサ C（無極性：セラミック／フィルム）

| Reference | 値 | フットプリント | 数量 |
|---|---|---|---|
| C21, C22, C3 | 0.001μF (1000pF) | C_Disc D5.0mm | 3 |
| C100, C101, C103, C111, C112, C113, C114, C115, C116, C117, C118, C119, C120, C121, C124, C125, C126 | 0.01μF | C_Disc D5.0mm | 17 |
| C4, C6, C7 | 0.1μF | C_Disc D5.0mm | 3 |
| C102, C104, C105, C122, C123 | 1μF | C_Disc D5.0mm | 5 |
| C9, C10 | 100pF | C_Disc D3.0mm | 2 |
| C11, C12, C14 | 47pF | C_Disc D3.0mm | 3 |
| C19, C20 | 33pF | C_Disc D3.0mm | 2 |
| C1, C2, C17, C18, C23, C24, C31 | 15pF | C_Disc D3.0mm | 7 |
| C13, C32 | 5pF | C_Disc D3.0mm | 2 |

**無極性コンデンサ 合計: 44個**

---

## コンデンサ C（電解：有極性）

| Reference | 値 | フットプリント | 数量 |
|---|---|---|---|
| C5, C8, C8b1 | 10μF | CP_Radial D5.0mm P2.00mm | 3 |
| C28, C30 | 100μF | CP_Radial D6.3mm P2.50mm | 2 |
| C158, C159, C160, C161, C162, C163, C164, C165, C166, C167, C168 | 1μF | CP_Radial D5.0mm P2.00mm | 11 |

**電解コンデンサ 合計: 16個**

---

## トリマコンデンサ TC

| Reference | 値 | フットプリント | 数量 |
|---|---|---|---|
| TC1, TC2 | 40pF | PSN_TRX:C_Trimmer_TMCV01 | 2 |

---

## コイル L・インダクタ

| Reference | 値 | フットプリント | 数量 | 説明 |
|---|---|---|---|---|
| L1, L2, L6, L7, L11, L12, L13 | 7T50 | PSN_TRX:L_FCZ07S_CT | 7 | FCZ07S コイル（センタータップ付） |
| L3 | 7T5 | PSN_TRX:L_FCZ07S_CT | 1 | FCZ07S コイル |
| L4 | T-30-10 6T/0.4mm | PSN_TRX:L_T30_2pin_Vertical | 1 | T-30 トロイダルコア 6巻 |
| L5 | T-30-10 6T+1T/0.4mm | PSN_TRX:L_T30_3pin_Vertical | 1 | T-30 トロイダルコア タップ付 |
| L9, L10 | 1mH | PSN_TRX:L_AL0510-153K_Vertical | 2 | AL0510-153K 縦型インダクタ |
| L8 | 15mH | PSN_TRX:L_AL0510-153K_Vertical | 1 | AL0510-153K 縦型インダクタ |
| L14, L15 | T-50-10 18T/0.4mm | PSN_TRX:L_T50_2pin_Vertical | 2 | T-50 トロイダルコア 18巻 |
| RFC1 | 10μH | PSN_TRX:L_AL0510-153K_Vertical | 1 | ドレイン側 RFチョーク（1W PA） |

---

## ダイオード D

| Reference | 値 | フットプリント | 数量 | 備考 |
|---|---|---|---|---|
| D1, D2, D3, D4, D7, D8 | 1N60 | D_DO-35 縦型 CathodeUp | 6 | ゲルマニウム検波ダイオード |

---

## トランジスタ Q

| Reference | 型番 | パッケージ | 数量 | 種別・備考 |
|---|---|---|---|---|
| **Q3** | **BF998** | **SOT-143 (SMD)** | **1** | **RF デュアルゲート N-ch MOSFET（2026-06-17 変更）** |
| Q4, Q11, Q12, Q13, Q15, Q17 | 2SC1815 | TO-92 | 6 | NPN 汎用トランジスタ |
| Q9, Q10, Q14 | 2SK439 | TO-92 | 3 | N-ch JFET |
| Q5 | 2SC2120 | TO-92 | 1 | NPN 中電力トランジスタ |
| Q6 | 2SA950 | TO-92 | 1 | PNP 中電力トランジスタ |
| Q2, Q7 | 2SC1923 | TO-92 | 2 | NPN 高周波トランジスタ |
| **Q8** | **RD06HVF1** | **TO-220F** | **1** | **1W PA 終段 RF N-ch MOSFET（175MHz, 6W）（2026-06-17 変更）** |

---

## IC・モジュール

| Reference | 型番 | パッケージ | 数量 | 説明 |
|---|---|---|---|---|
| IC1 | LP2950L-5.0V | TO-92 | 1 | 5V 三端子レギュレータ |
| IC2 | NJM2904 | DIP-8 | 3 | デュアル OP アンプ |
| U2 | AE-Si5351A | DIP-8 変換基板 | 1 | I2C クロックジェネレーターモジュール |
| A1 | XIAO ESP32C3 | ソケット実装 | 1 | Seeed Studio XIAO ESP32C3（VFO 制御） |

---

## トランス T

| Reference | 型番 | フットプリント | 数量 | 説明 |
|---|---|---|---|---|
| T1 | ST-71 | PSN_TRX:Transformer_ST71_CB19 | 1 | 山水 ST-71（音声トランス、CB-19 リード型） |

---

## リレー K

| Reference | 型番 | フットプリント | 数量 | 説明 |
|---|---|---|---|---|
| K1 | G5V-2 | Relay_DPDT_Omron_G5V-2 | 1 | オムロン DPDT リレー（TX/RX 切替） |

---

## 水晶振動子 X

| Reference | 値 | フットプリント | 数量 | 説明 |
|---|---|---|---|---|
| X1 | 50.5MHz/3 | Crystal_HC49-4H_Vertical | 1 | HC49 縦型水晶（VXO 用、約 16.833MHz） |

---

## LED

| Reference | 値 | フットプリント | 数量 |
|---|---|---|---|
| LED1 | LED（赤） | PinHeader_1x02 P2.54mm（外付け） | 1 |
| LED2 | LED（黄） | PinHeader_1x02 P2.54mm（外付け） | 1 |

---

## スイッチ SW

| Reference | 型番 | フットプリント | 数量 |
|---|---|---|---|
| SW1, SW2 | DIP スライドスイッチ | SW_DIP_SPSTx01_Slide_6.7x4.1mm | 2 |

---

## コネクタ J

| Reference | 機能 | フットプリント | 数量 |
|---|---|---|---|
| J1, J2, J3 | PWR_IN（電源入力） | PinHeader_1x02 P2.54mm | 3 |
| J4 | MIC-IN（マイク入力） | PinHeader_1x02 P2.54mm | 1 |
| J5 | FREQ-VC | PinHeader_1x02 P2.54mm | 1 |
| J6 | Volume（音量） | PinHeader_1x03 P2.54mm | 1 |

---

## 部品点数サマリ

| カテゴリ | 種類数 | 合計数量 |
|---|---|---|
| 固定抵抗 | 13 種 | 43 本 |
| 1W PA バイアス抵抗 | 3 種 | 3 本 |
| 可変抵抗・トリマポット | 4 種 | 5 個 |
| 無極性コンデンサ | 9 種 | 44 個 |
| 電解コンデンサ | 3 種 | 16 個 |
| トリマコンデンサ | 1 種 | 2 個 |
| FCZ07S コイル | 2 値 | 8 個 |
| トロイダルコイル（T-30/T-50） | 3 種 | 4 個 |
| 固定インダクタ（AL0510） | 2 値 | 3 個 |
| RFチョーク | 1 種 | 1 個 |
| ゲルマニウムダイオード | 1 種 | 6 個 |
| トランジスタ（BJT/JFET/MOSFET） | 7 種 | 15 個 |
| IC | 2 種 | 4 個 |
| モジュール（AE-Si5351A） | 1 種 | 1 個 |
| マイコンモジュール（XIAO ESP32C3） | 1 種 | 1 個 |
| 音声トランス | 1 種 | 1 個 |
| リレー | 1 種 | 1 個 |
| 水晶振動子 | 1 種 | 1 個 |
| LED | 2 種 | 2 個 |
| スイッチ | 1 種 | 2 個 |
| コネクタ（ピンヘッダ） | 4 種 | 6 個 |

---

## 注意事項

- **kicad/ フォルダが最新版**。`transceiver/` フォルダは旧設計のため参照不要。
- **Q3 (BF998)** は SMD（SOT-143）部品。手実装の場合ピン配置に注意。
- **Q8 (RD06HVF1)** は 12V 動作の RF MOSFET。TO-220F パッケージ（絶縁型）。ドレインへの放熱対策を施すこと。
- **R20 (0R)** はジャンパ線での代替可能。
- **VR3** は Bourns 3266W 500Ω トリマポット。Idq を 50〜80mA に調整する。
- **AE-Si5351A** は Aitendo 等で入手可能な I2C クロックジェネレーターモジュール（DIP-8 変換基板付き）。

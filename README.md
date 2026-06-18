# PSN_TRX_XIAO_ESP32C3

Arduino Nano R4 + Seeed Studio XIAO ESP32C3 + Si5351 を使用した PSN 方式 SSB トランシーバー（KiCad 10.0）。

## 概要

50MHz 帯 PSN（位相シフト網）方式 SSB トランシーバー。VXO（水晶発振器）を
Si5351A クロックジェネレーターによる VFO に置き換え、Arduino Nano R4 でデジタル制御する。

Si5351 の CLK0（0°）/ CLK1（90°）二相出力を直接バランスドモジュレーターへ供給することで、
従来の RF PSN（LC 位相シフト回路）も不要となる。

## 主な仕様

| 項目 | 内容 |
|---|---|
| 周波数範囲 | 50.000 〜 51.000 MHz（6m バンド） |
| CLK0 出力 | 0° キャリア → C21（バランスドモジュレーター） |
| CLK1 出力 | 90° キャリア → C22（バランスドモジュレーター） |
| チューニングステップ | 10Hz / 100Hz / 1kHz / 10kHz / 100kHz |
| 表示 | OLED SSD1306 128×64 |
| 周波数記憶 | NVS（電源 OFF 後も保持） |

## ハードウェア構成

```
Arduino Nano R4
├── Seeed Studio XIAO ESP32C3 ─ サブコントローラ
├── Si5351A モジュール (AE-Si5351A) ─ I2C クロックジェネレーター
│   ├── CLK0（0°）  → バランスドモジュレーター C21
│   └── CLK1（90°） → バランスドモジュレーター C22
└── OLED / ロータリーエンコーダ 等

1W PA: RD06HVF1 (N-ch RF MOSFET) @ 12V, Class AB
```

## 1W パワーアンプ（Q8）

前段（2SC1815 等）の出力（約 20〜30mW）を増幅する終段アンプ。

| 項目 | 内容 |
|---|---|
| トランジスタ | **RD06HVF1**（三菱電機 N-ch RF MOSFET, 175MHz, 6W, TO-220F） |
| 電源電圧 | 12V |
| 動作クラス | Class AB |
| 静止電流 Idq | 200〜400mA（VR3 で調整） |
| 出力 | 約 1W @50MHz |
| 出力 LPF | 56pF → 270nH → 56pF（カットオフ約 60MHz） |

### バイアス回路

```
VCC(12V) → R22(470Ω) ─┬─ VR3(500Ω) → GND
                       │    ↓（ワイパー）
                       └── R21(10Ω) → Q8ゲート
```

- VR3 を中間位置でゲート電圧 ≈ **3.1V** → RD06HVF1 の Class AB 動作に最適
- VR3 を徐々に回してドレイン電流 (Idq) 200〜400mA に合わせる
- D3, D4（旧バイアスダイオード）は **0R ショート**（MOSFET では不要）
- R20（旧エミッタ抵抗 10Ω）は **0R ショート**（ソース直結 GND）

詳細は `docs/PSN_TRX_VFO改造仕様書.docx` を参照。

## KiCad ライブラリ状態

| ファイル | 状態 |
|---|---|
| `kicad/PSN_TRX.pretty/` | 全12フットプリント KiCad 10 形式 ✅ |
| `kicad/PSN_TRX.kicad_sym` | カスタムシンボル（RD06HVF1 含む）✅ |
| `kicad/fp-lib-table` | PSN_TRX ライブラリ登録済み ✅ |
| DRC ライブラリエラー | **0件** ✅ |

## ファイル構成

```
kicad/
  PSN_TRX.kicad_sch       - 回路図
  PSN_TRX.kicad_pcb       - PCB レイアウト（配線作業中）
  PSN_TRX.kicad_sym       - カスタムシンボルライブラリ
  PSN_TRX.pretty/         - カスタムフットプリントライブラリ（12点）
  BOM.md                  - 部品表
docs/
  PSN_TRX_VFO改造仕様書.docx  - 改造仕様書（部品リスト・回路図含む）
```

## 変更履歴

| 日付 | 変更内容 |
|---|---|
| 2026-06-17 | Q3: 3SK59(TO-72 THT) → BF998(SOT-143 SMD)、カスタムシンボル・FP追加 |
| 2026-06-17 | Q8: 2SC1971 → RD06HVF1 (RF MOSFET) 換装、バイアス回路変更 |
| 2026-06-17 | KiCad 10 フットプリントライブラリ全面更新（12ファイル） |
| 2026-06-17 | U2: DIP-12 → DIP-8 フットプリント修正（AE-Si5351A 実寸合わせ） |

## ライセンス

MIT License

## 作者

JA3 (kazushinjo)

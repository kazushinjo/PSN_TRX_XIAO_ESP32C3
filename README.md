# PSN_TRX_ESP32

ESP32 + Si5351 を使用した PSN 方式 SSB トランシーバー用 VFO

## 概要

既存の PSN 方式 SSB トランシーバーの VXO（水晶発振器）および RF PSN パッシブ回路を、
ESP32 マイコンと Si5351 クロックジェネレーターによる VFO に置き換えるプロジェクト。

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
ESP32 DevKit
├── Si5351A モジュール（I2C: SDA=GPIO21, SCL=GPIO22）
├── OLED SSD1306 128x64（I2C: 同上）
└── ロータリーエンコーダ（A=GPIO32, B=GPIO33, SW=GPIO25）

Si5351 CLK0 → π型LPF → レベル調整（470Ω/47Ω) → C21
Si5351 CLK1 → π型LPF → レベル調整（470Ω/47Ω) → C22
```

## 必要ライブラリ

Arduino IDE のライブラリマネージャーからインストール：

- **Etherkit Si5351** by Jason Milldrum
- **Adafruit SSD1306** by Adafruit
- **Adafruit GFX Library** by Adafruit

## 接続図

```
ESP32 GPIO21 (SDA) ─── Si5351 SDA
                   └── OLED SDA
ESP32 GPIO22 (SCL) ─── Si5351 SCL
                   └── OLED SCL
ESP32 GPIO32       ─── Encoder A
ESP32 GPIO33       ─── Encoder B
ESP32 GPIO25       ─── Encoder SW
```

## LPF / レベル調整回路

Si5351 の矩形波出力を正弦波化し、適切なレベルに調整する。

```
Si5351 CLK ─┬─ 100nH ─┬─ 470Ω ─┬── C21/C22入力
            │          │         47Ω
           47pF       47pF        │
            │          │         GND
           GND        GND
```

## 1W パワーアンプ（オプション）

既存終段（2SC1815）の出力（約20〜30mW）を増幅する。

- トランジスタ：2SC1971
- 出力：約 1W（@12V、クラスAB）
- 出力 LPF：56pF → 270nH → 56pF（カットオフ約 60MHz）

詳細は `docs/PSN_TRX_VFO改造仕様書.docx` を参照。

## ファイル構成

```
PSN_TRX_ESP32.ino        - Arduino スケッチ（メイン）
docs/
  PSN_TRX_VFO改造仕様書.docx  - 改造仕様書（部品リスト・回路図含む）
```

## ライセンス

MIT License

## 作者

JA3 (kazushinjo)

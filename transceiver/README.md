# PSN_TRX

PSN（位相シフト網）方式 SSB トランシーバの回路図プロジェクト（KiCad 10.0）。
50MHz 帯・VXO 制御。`PSN_TRX.kicad_sch` を手作業で作図中。

- リポジトリ: `kazushinjo/PSN_TRX_New`（Private）
- ローカル作業: `C:\Users\shinjo\OneDrive\デスクトップ\KiCad\PSN_TRX`

> ⚠️ **作業中** — まだ若干の回路追加が予定されています。追加完了後に続きの作業を進めます。

---

## リポジトリ構成

```
PSN_TRX/
├── PSN_TRX.kicad_sch          回路図本体
├── PSN_TRX.kicad_pro          プロジェクト設定
├── PSN_TRX.pretty/            自作フットプリント
│   ├── C_Trimmer_TMCV01.kicad_mod
│   ├── Transformer_ST71_CB19.kicad_mod
│   └── L_AL0510-153K_Vertical.kicad_mod
├── fp-lib-table               フットプリントライブラリ登録（${KIPRJMOD}/PSN_TRX.pretty）
├── *.py                       回路図生成・編集スクリプト（下記）
└── README.md
```

`*.kicad_prl` / `*.bak` / `*.lck` / `.history/` / `PSN_TRX-backups/` は `.gitignore` で除外。

---

## 主要コンポーネント（概算）

| 種別 | シンボル | 数 |
|---|---|---|
| 固定抵抗 | `Device:R` | 40 |
| 可変抵抗・ポット | `Device:R_Potentiometer` | 5 |
| コンデンサ | `Device:C` | 55 |
| トリマコンデンサ | `Device:C_Variable`（TC1, TC2） | 2 |
| ダイオード（1N60 ゲルマ検波） | `Device:D` | 6 |
| LED | `Device:LED` | 2 |
| トランス（7T50 等） | `Device:Transformer_1P_1S` | 9 |
| トランス（ST-71, CT付） | `Device:Transformer_1P_SS`（T1） | 1 |
| インダクタ | `Device:L`（L8 ほか） | — |
| トランジスタ | `Transistor_*` / `Device:Q_*` | 16 |
| OPアンプ | `Amplifier_Operational:LM2904`（NJM2904） | — |
| 水晶 | `Device:Crystal` | 1 |
| 三端子レギュレータ | `Regulator_Linear:MC78L05_TO92` | 1 |
| スイッチ | `Switch:SW_SPDT` / `SW_SPST` | 3 |

主要ブロックに「AF PSN・信号分割」セクション（ST-71 トランス T1 ＋ NJM2904 による音声位相分割）あり。

---

## フットプリント割り当て状況

### 割り当て済み ✅

| 部品 | フットプリント | 備考 |
|---|---|---|
| TC1 / TC2（トリマC 40p/5p） | `PSN_TRX:C_Trimmer_TMCV01` | Topmay TMCV01 |
| T1（ST-71 音声トランス） | `PSN_TRX:Transformer_ST71_CB19` | 山水 ST-71・CB-19 **リード型**・二次CT |
| L8（15mH インダクタ） | `PSN_TRX:L_AL0510-153K_Vertical` | AL0510-153K・**縦実装** |
| 固定抵抗 40個 | `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical` | 1/4W・**縦実装** |
| ダイオード 6個（1N60） | `Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_CathodeUp` | DO-35・**縦実装** |

### 未割り当て ⏳
コンデンサ（55）／可変抵抗・ポット（5）／LED（2）／7T50系トランス（9）／トランジスタ（16）／OPアンプ／水晶／レギュレータ／スイッチ（3）

---

## 自作フットプリント（`PSN_TRX.pretty/`）

| 名称 | 内容 |
|---|---|
| `C_Trimmer_TMCV01` | Topmay TMCV01 セラミックトリマC（本体6×6mm, ピッチ5mm, ドリル1.2mm） |
| `Transformer_ST71_CB19` | 山水 ST-71（CB-19リード型）。pad 1,2=一次／3,4,5=二次（4=CT）。ピッチ I=8/G=14, 行間 C=16.5mm |
| `L_AL0510-153K_Vertical` | AL0510-153K 軸形インダクタ縦実装。本体D5×L14mm, リードピッチ P=2.54mm |

抵抗・ダイオードは KiCad 標準ライブラリ（`Resistor_THT` / `Diode_THT`、global fp-lib-table 登録済）を参照。

---

## スクリプト

| ファイル | 役割 |
|---|---|
| `generate_schematic.py` / `_v2.py` | 元 JPG 回路図からの初期生成（絶対座標配置） |
| `add_connections.py` / `add_wiring.py` | 配線追加 |
| `add_c13_c14.py` / `add_l4_l5.py` / `add_tc1_tc2.py` | 個別部品の追加 |
| `add_st71.py` | L8→T1 変換（reference/value/センタータップシンボル/FP 割当） |
| `set_vertical_footprints.py` | Device:R / Device:D へ縦実装FPを一括割当 |

> スクリプトは `.kicad_sch` を直接書き換えます。**実行前に KiCad を閉じる**こと。実行後は KiCad で開き直して確認。

---

## 残作業 / TODO

- [ ] 残りの回路を追加（予定）
- [ ] 未割り当て部品のフットプリント設定（C / 可変抵抗 / LED / 7T50トランス / トランジスタ / OPアンプ / 水晶 / レギュレータ / SW）
- [ ] ダイオードの向き（現状 CathodeUp）を回路に合わせて個別確認
- [ ] 抵抗サイズ（1/4W 前提）で 1/8W・1/2W があれば個別差し替え
- [ ] ERC / アノテーションの整理
- [ ] PCB レイアウト着手

---

## 環境・注意

- KiCad 10.0 / Windows 11
- ローカルが **OneDrive 配下**のため、git 同期と OneDrive 同期の競合（`.git` 内ロック等）に注意
- 配線は手動で実施

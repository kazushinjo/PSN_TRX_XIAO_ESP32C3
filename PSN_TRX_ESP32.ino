/*
 * PSN TRX VFO - ESP32 + Si5351 (二相出力 / Quadrature)
 * 50.000 ~ 51.000 MHz
 *
 * Libraries (install via Arduino IDE Library Manager):
 *   - "Etherkit Si5351" by Jason Milldrum
 *   - "Adafruit SSD1306" by Adafruit
 *   - "Adafruit GFX Library" by Adafruit
 *
 * Wiring:
 *   Si5351 SDA  -> GPIO21
 *   Si5351 SCL  -> GPIO22
 *   OLED  SDA   -> GPIO21
 *   OLED  SCL   -> GPIO22
 *   Encoder A   -> GPIO32
 *   Encoder B   -> GPIO33
 *   Encoder SW  -> GPIO25
 *
 *   Si5351 CLK0 (0°)  -> 100pF -> L6 -> Q9 バランスドモジュレーター
 *   Si5351 CLK1 (90°) -> 100pF -> L7 -> Q10 バランスドモジュレーター
 *
 *   RF PSN パッシブ回路（LC位相シフト網）は不要・削除可
 *
 * 動作原理:
 *   Si5351 の CLK0/CLK1 は同一 PLL A を整数分周(÷16)で使用し
 *   位相レジスタにより正確な 90° 位相差を実現する。
 *   分周比 16 → PLL = 800〜816 MHz (50〜51MHz 全域で有効)
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <si5351.h>
#include <Preferences.h>

// ---- OLED ----
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ---- Si5351 ----
Si5351 si5351;

// ---- Rotary Encoder ----
#define ENC_A  32
#define ENC_B  33
#define ENC_SW 25

// ---- 周波数設定 ----
#define FREQ_MIN  50000000L   // 50.000 MHz
#define FREQ_MAX  51000000L   // 51.000 MHz
#define FREQ_DEFAULT 50500000L // 50.500 MHz

long currentFreq = FREQ_DEFAULT;

// ---- ステップ ----
const long   stepValues[] = {10, 100, 1000, 10000, 100000};
const char*  stepLabels[] = {"  10Hz", " 100Hz", "  1kHz", " 10kHz", "100kHz"};
const int    stepCount    = 5;
int stepIndex = 2; // デフォルト 1kHz

// ---- エンコーダ ----
volatile int encCount  = 0;
int          lastCount = 0;

// ---- ボタン ----
bool         lastBtnState  = HIGH;
unsigned long lastBtnTime  = 0;

// ---- NVS（周波数記憶） ----
Preferences prefs;

// ---- ISR ----
void IRAM_ATTR encoderISR() {
  static int lastA = HIGH;
  int a = digitalRead(ENC_A);
  int b = digitalRead(ENC_B);
  if (a != lastA) {
    encCount += (b != a) ? 1 : -1;
    lastA = a;
  }
}

// ---- Si5351 二相出力（CLK0=0° / CLK1=90°） ----
// PLL A を整数分周(÷16)で両クロックに共用し位相レジスタで 90° をセット
#define QUAD_DIV 16  // 50MHz×16=800MHz, 51MHz×16=816MHz (PLL範囲内)

void setFrequency(long freq) {
  uint64_t f   = (uint64_t)freq * 100ULL;       // 1/100 Hz 単位
  uint64_t pll = f * QUAD_DIV;                   // PLL 周波数

  // 両クロックを PLL A・同一整数分周で設定
  si5351.set_freq_manual(f, pll, SI5351_CLK0);
  si5351.set_freq_manual(f, pll, SI5351_CLK1);

  // CLK0 = 0°、CLK1 = 90°（位相レジスタ値 = DIV/4）
  si5351.set_phase(SI5351_CLK0, 0);
  si5351.set_phase(SI5351_CLK1, QUAD_DIV / 4);  // = 4

  // 位相設定を反映するため PLL リセット
  si5351.pll_reset(SI5351_PLLA);
}

// ---- OLED 表示更新 ----
void updateDisplay() {
  display.clearDisplay();

  // 周波数 (大文字)
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 4);

  long f   = currentFreq;
  int  mhz = f / 1000000;
  int  khz = (f % 1000000) / 1000;
  int  hz  = f % 1000;

  char buf[24];
  sprintf(buf, "%2d.%03d.%03d", mhz, khz, hz);
  display.print(buf);

  // 単位
  display.setTextSize(1);
  display.setCursor(108, 10);
  display.print("MHz");

  // 区切り線
  display.drawLine(0, 28, 127, 28, SSD1306_WHITE);

  // ステップ表示
  display.setTextSize(1);
  display.setCursor(0, 34);
  display.print("STEP:");
  display.print(stepLabels[stepIndex]);

  // バンド表示
  display.setCursor(0, 50);
  display.print("50MHz Band  6m");

  display.display();
}

// ---- NVS 保存 ----
void saveFreq() {
  prefs.begin("vfo", false);
  prefs.putLong("freq", currentFreq);
  prefs.putInt("step", stepIndex);
  prefs.end();
}

// ---- NVS 読み込み ----
void loadFreq() {
  prefs.begin("vfo", true);
  currentFreq = prefs.getLong("freq", FREQ_DEFAULT);
  stepIndex   = prefs.getInt("step", 2);
  prefs.end();

  // 範囲チェック
  if (currentFreq < FREQ_MIN || currentFreq > FREQ_MAX)
    currentFreq = FREQ_DEFAULT;
  if (stepIndex < 0 || stepIndex >= stepCount)
    stepIndex = 2;
}

// ============================================================
void setup() {
  Serial.begin(115200);

  // エンコーダ
  pinMode(ENC_A,  INPUT_PULLUP);
  pinMode(ENC_B,  INPUT_PULLUP);
  pinMode(ENC_SW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, CHANGE);

  // I2C (SDA=21, SCL=22)
  Wire.begin(21, 22);

  // OLED 初期化
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED not found");
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(20, 28);
  display.print("PSN TRX VFO");
  display.display();
  delay(1000);

  // Si5351 初期化 (25MHz 基準水晶)
  if (!si5351.init(SI5351_CRYSTAL_LOAD_8PF, 25000000, 0)) {
    Serial.println("Si5351 not found");
  }
  si5351.drive_strength(SI5351_CLK0, SI5351_DRIVE_8MA);
  si5351.drive_strength(SI5351_CLK1, SI5351_DRIVE_8MA);
  si5351.output_enable(SI5351_CLK2, 0);

  // NVS から周波数復元
  loadFreq();

  setFrequency(currentFreq);
  updateDisplay();
}

// ============================================================
void loop() {
  // ---- エンコーダ処理 ----
  int cnt = encCount;
  if (cnt != lastCount) {
    int diff = cnt - lastCount;
    currentFreq += (long)diff * stepValues[stepIndex];

    if (currentFreq < FREQ_MIN) currentFreq = FREQ_MIN;
    if (currentFreq > FREQ_MAX) currentFreq = FREQ_MAX;

    lastCount = cnt;
    setFrequency(currentFreq);
    updateDisplay();
    saveFreq(); // 変更のたびに保存
  }

  // ---- ボタン処理（ステップ切替） ----
  bool btn = digitalRead(ENC_SW);
  if (btn == LOW && lastBtnState == HIGH) {
    unsigned long now = millis();
    if (now - lastBtnTime > 200) {
      stepIndex = (stepIndex + 1) % stepCount;
      updateDisplay();
      saveFreq();
      lastBtnTime = now;
    }
  }
  lastBtnState = btn;

  delay(1);
}

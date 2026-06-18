/*
 * PSN TRX VFO - Seeed Studio XIAO ESP32C3 (RISC-V 32-bit 160MHz) + Si5351
 * 50.000 ~ 51.000 MHz (6m Band)
 *
 * ---- コンパイル時ディスプレイ選択 ----
 *   #define USE_TJC_DISPLAY  → TJC4832T135  Serial1: D6(TX) D7(RX)
 *   コメントアウト           → SSD1306 OLED I2C: D4(SDA) D5(SCL)
 *
 * ---- TJC HMI 画面構成 (TJC USART HMI Editor で作成) ----
 *   t0 : 周波数表示  (大テキスト)
 *   t1 : ステップ表示
 *   t2 : 固定情報    (TJC_FIXED_LINE1 / LINE2 で内容を指定)
 *
 * Libraries:
 *   - Etherkit Si5351
 *   - Adafruit SSD1306 / Adafruit GFX  (OLED使用時のみ必要)
 *   - Preferences  (ESP32 標準内蔵・NVS フラッシュ保存)
 *
 * Wiring (XIAO ESP32C3):
 *   Si5351 SDA  -> D4 (GPIO6)
 *   Si5351 SCL  -> D5 (GPIO7)
 *   OLED  SDA   -> D4 (GPIO6)   ※ OLED使用時
 *   OLED  SCL   -> D5 (GPIO7)   ※ OLED使用時
 *   Encoder A   -> D0 (GPIO2)
 *   Encoder B   -> D1 (GPIO3)
 *   Encoder SW  -> D2 (GPIO4)
 *   TJC TX      -> D6 (GPIO21)  ※ TJC使用時
 *   TJC RX      -> D7 (GPIO20)  ※ TJC使用時
 */

// ============================================================
// ★ ここを編集してディスプレイを選択
// ============================================================
#define USE_TJC_DISPLAY

// TJC固定表示文字列（内容未定のため仮。確定後に変更）
#define TJC_FIXED_LINE1  "6m PSN TRX"
#define TJC_FIXED_LINE2  ""
// ============================================================

#include <Wire.h>
#include <si5351.h>
#include <Preferences.h>

#ifndef USE_TJC_DISPLAY
  #include <Adafruit_GFX.h>
  #include <Adafruit_SSD1306.h>
  #define SCREEN_WIDTH  128
  #define SCREEN_HEIGHT  64
  Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
#endif

// ---- Si5351 ----
Si5351 si5351;

// ---- Preferences (NVS) ----
Preferences prefs;

// ---- Rotary Encoder ----
#define ENC_A  D0
#define ENC_B  D1
#define ENC_SW D2

// ---- 周波数設定 ----
#define FREQ_MIN     50000000L
#define FREQ_MAX     51000000L
#define FREQ_DEFAULT 50500000L

long currentFreq = FREQ_DEFAULT;

// ---- ステップ ----
const long  stepValues[] = {10, 100, 1000, 10000, 100000};
const char* stepLabels[] = {"10Hz", "100Hz", "1kHz", "10kHz", "100kHz"};
const int   stepCount    = 5;
int stepIndex = 2;

// ---- エンコーダ ----
volatile int encCount  = 0;
int          lastCount = 0;

// ---- ボタン ----
bool          lastBtnState = HIGH;
unsigned long lastBtnTime  = 0;

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

// ---- Si5351 二相出力 ----
#define QUAD_DIV 16

void setFrequency(long freq) {
  uint64_t f   = (uint64_t)freq * 100ULL;
  uint64_t pll = f * QUAD_DIV;
  si5351.set_freq_manual(f, pll, SI5351_CLK0);
  si5351.set_freq_manual(f, pll, SI5351_CLK1);
  si5351.set_phase(SI5351_CLK0, 0);
  si5351.set_phase(SI5351_CLK1, QUAD_DIV / 4);
  si5351.pll_reset(SI5351_PLLA);
}

// ============================================================
// TJC4832T135 ドライバ
// ============================================================
#ifdef USE_TJC_DISPLAY

void tjcSend(const char* cmd) {
  Serial1.print(cmd);
  Serial1.write(0xFF);
  Serial1.write(0xFF);
  Serial1.write(0xFF);
}

void tjcSetText(const char* component, const char* value) {
  char buf[80];
  snprintf(buf, sizeof(buf), "%s.txt=\"%s\"", component, value);
  tjcSend(buf);
}

void tjcInit() {
  // ESP32C3: D6=GPIO21(TX), D7=GPIO20(RX)
  Serial1.begin(9600, SERIAL_8N1, D7, D6);
  delay(500);
  tjcSend("baud=9600");
  tjcSend("page 0");
  char fixed[48];
  if (strlen(TJC_FIXED_LINE2) > 0)
    snprintf(fixed, sizeof(fixed), "%s  %s", TJC_FIXED_LINE1, TJC_FIXED_LINE2);
  else
    snprintf(fixed, sizeof(fixed), "%s", TJC_FIXED_LINE1);
  tjcSetText("t2", fixed);
}

void updateDisplay() {
  long f   = currentFreq;
  int  mhz = f / 1000000;
  int  khz = (f % 1000000) / 1000;
  int  hz  = f % 1000;

  char freqBuf[24];
  snprintf(freqBuf, sizeof(freqBuf), "%d.%03d.%03d MHz", mhz, khz, hz);
  tjcSetText("t0", freqBuf);

  char stepBuf[20];
  snprintf(stepBuf, sizeof(stepBuf), "STEP: %s", stepLabels[stepIndex]);
  tjcSetText("t1", stepBuf);
}

// ============================================================
// SSD1306 OLED ドライバ
// ============================================================
#else

void updateDisplay() {
  oled.clearDisplay();
  oled.setTextSize(2);
  oled.setTextColor(SSD1306_WHITE);
  oled.setCursor(0, 4);

  long f   = currentFreq;
  int  mhz = f / 1000000;
  int  khz = (f % 1000000) / 1000;
  int  hz  = f % 1000;

  char buf[24];
  sprintf(buf, "%2d.%03d.%03d", mhz, khz, hz);
  oled.print(buf);

  oled.setTextSize(1);
  oled.setCursor(108, 10);
  oled.print("MHz");

  oled.drawLine(0, 28, 127, 28, SSD1306_WHITE);

  oled.setTextSize(1);
  oled.setCursor(0, 34);
  oled.print("STEP: ");
  oled.print(stepLabels[stepIndex]);

  oled.setCursor(0, 50);
  oled.print("50MHz Band  6m");

  oled.display();
}

#endif  // USE_TJC_DISPLAY

// ---- NVS 保存 ----
void saveFreq() {
  prefs.begin("psn_trx", false);
  prefs.putLong("freq", currentFreq);
  prefs.putInt("step", stepIndex);
  prefs.end();
}

// ---- NVS 読み込み ----
void loadFreq() {
  prefs.begin("psn_trx", true);
  currentFreq = prefs.getLong("freq", FREQ_DEFAULT);
  stepIndex   = prefs.getInt("step", 2);
  prefs.end();

  if (currentFreq < FREQ_MIN || currentFreq > FREQ_MAX)
    currentFreq = FREQ_DEFAULT;
  if (stepIndex < 0 || stepIndex >= stepCount)
    stepIndex = 2;
}

// ============================================================
void setup() {
  Serial.begin(115200);

  pinMode(ENC_A,  INPUT_PULLUP);
  pinMode(ENC_B,  INPUT_PULLUP);
  pinMode(ENC_SW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, CHANGE);

  Wire.begin();

#ifdef USE_TJC_DISPLAY
  tjcInit();
#else
  if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C))
    Serial.println("OLED not found");
  oled.clearDisplay();
  oled.setTextColor(SSD1306_WHITE);
  oled.setTextSize(1);
  oled.setCursor(20, 28);
  oled.print("PSN TRX VFO");
  oled.display();
  delay(1000);
#endif

  if (!si5351.init(SI5351_CRYSTAL_LOAD_8PF, 25000000, 0))
    Serial.println("Si5351 not found");
  si5351.drive_strength(SI5351_CLK0, SI5351_DRIVE_8MA);
  si5351.drive_strength(SI5351_CLK1, SI5351_DRIVE_8MA);
  si5351.output_enable(SI5351_CLK2, 0);

  loadFreq();
  setFrequency(currentFreq);
  updateDisplay();
}

// ============================================================
void loop() {
  int cnt = encCount;
  if (cnt != lastCount) {
    int diff = cnt - lastCount;
    currentFreq += (long)diff * stepValues[stepIndex];
    if (currentFreq < FREQ_MIN) currentFreq = FREQ_MIN;
    if (currentFreq > FREQ_MAX) currentFreq = FREQ_MAX;
    lastCount = cnt;
    setFrequency(currentFreq);
    updateDisplay();
    saveFreq();
  }

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

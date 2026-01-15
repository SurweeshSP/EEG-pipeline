/*
 * NEUROSENSE AI - BioAmp EXG Pill Streaming
 * Streams 1-channel EEG data over Serial at 500 Hz
 * 
 * Hardware:
 * - Arduino Uno R3
 * - BioAmp EXG Pill
 * 
 * Connections:
 * - BioAmp VCC → Arduino 5V
 * - BioAmp GND → Arduino GND
 * - BioAmp OUT → Arduino A0
 */

// Configuration
#define ANALOG_PIN A0
#define SAMPLING_RATE 500  // Hz
#define SAMPLE_INTERVAL_US (1000000 / SAMPLING_RATE)

unsigned long lastSampleTime = 0;
int sampleValue = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Configure analog input
  pinMode(ANALOG_PIN, INPUT);
  
  // Set ADC reference to default (5V)
  analogReference(DEFAULT);
  
  // Wait for serial connection
  while (!Serial) {
    ; // Wait for serial port to connect
  }
  
  Serial.println("BioAmp EXG Pill streaming at 500 Hz, 1 channel");
  Serial.println("Channel: C3 (Left Motor Cortex)");
  
  // Sync time
  lastSampleTime = micros();
}

void loop() {
  unsigned long currentTime = micros();
  
  // Check if it's time to sample
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_US) {
    lastSampleTime = currentTime;
    
    // Read analog value (0-1023)
    sampleValue = analogRead(ANALOG_PIN);
    
    // Send via serial
    Serial.println(sampleValue);
  }
}

/*
 * Alternative: Higher quality with oversampling
 * Uncomment below for better SNR (reduces effective rate to 250 Hz)
 */

/*
void loop() {
  unsigned long currentTime = micros();
  
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_US * 2) {
    lastSampleTime = currentTime;
    
    // Oversample 4× and average
    long sum = 0;
    for (int i = 0; i < 4; i++) {
      sum += analogRead(ANALOG_PIN);
      delayMicroseconds(50);
    }
    sampleValue = sum / 4;
    
    Serial.println(sampleValue);
  }
}
*/

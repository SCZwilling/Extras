#include <MPU9250_WE.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

#define DEBUG 1

#if DEBUG == 1
#define SERIAL_BEGIN(X) Serial.begin(X)
#define SERIAL_PRINT(X) Serial.print(X)
#define SERIAL_PRINT_LN(X) Serial.println(X)
#else
#define SERIAL_BEGIN(X)
#define SERIAL_PRINT(X)
#define SERIAL_PRINT_LN(X)
#endif

const char* ssid = "admin_ncair";
const char* password = "Admin@123Ncair";

// Define Client
WiFiUDP ntpUDP;
WiFiClient client;
HTTPClient http;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

// Variables
String formattedDate;
uint8_t currentMotorStatus;
String macAddress;

const char* serverName = "https://twin.zwillinglabs.io/api/iot/data";  // FastAPI server
const int ctAnalogPin = 34;
const int csPin = 5;  // Chip Select Pin
bool useSPI = true;   // SPI use flag
const int sendDataTimerMS = 300000;
const int numSamples = 2000;
const int numValues = 7;
const int batchSize = 400;  // Number of samples per batch
int ctThreshold = 50;                 // Example threshold value (adjust based on your setup)
const int ctNumSamples = 100;           // Number of samples to take for RMS calculation
unsigned long ctSampleInterval = 500;  // Time interval for sampling (in microseconds)
uint8_t previousMotorStatus = 2; // Initialize to a value that is neither 0 nor 1
unsigned long sdPreviousMillis = 0;
int16_t accelGyroData[numSamples * numValues];  // Store raw values as 16-bit integers
int sampleCurrent[ctNumSamples];  // Declare array to store samples

MPU9250_WE myMPU9250 = MPU9250_WE(&SPI, csPin, useSPI);

void connectToWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    SERIAL_PRINT_LN("WiFi not connected. Attempting to connect...");
    WiFi.disconnect();  // Ensure a clean state
    WiFi.begin(ssid, password);

    unsigned long startAttemptTime = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
      delay(500);
      SERIAL_PRINT(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
      SERIAL_PRINT_LN("\nConnected to WiFi");
    } else {
      SERIAL_PRINT_LN("\nFailed to connect to WiFi");
    }
  }
}

String createJsonString(String batchId, int startIndex, int endIndex) {
  String jsonString = "{";

  // Add MAC address
  jsonString += "\"mac_address\":\"" + String(macAddress) + "\",";

  // Add data object
  jsonString += "\"data\":{";

  // Add mpu_burst array
  jsonString += "\"mpu_burst_new\":[{";
  jsonString += "\"batch_id\":\"" + batchId + "\"";
  jsonString += ",\"machine_status\":" + String(currentMotorStatus);
  jsonString += ",\"ax\":";
  jsonString += serializeRawArray(accelGyroData, 0, startIndex, endIndex, numValues);
  jsonString += ",\"ay\":";
  jsonString += serializeRawArray(accelGyroData, 1, startIndex, endIndex, numValues);
  jsonString += ",\"az\":";
  jsonString += serializeRawArray(accelGyroData, 2, startIndex, endIndex, numValues);
  jsonString += ",\"gx\":";
  jsonString += serializeRawArray(accelGyroData, 3, startIndex, endIndex, numValues);
  jsonString += ",\"gy\":";
  jsonString += serializeRawArray(accelGyroData, 4, startIndex, endIndex, numValues);
  jsonString += ",\"gz\":";
  jsonString += serializeRawArray(accelGyroData, 5, startIndex, endIndex, numValues);
  jsonString += ",\"ct\":";
  jsonString += serializeRawArray(accelGyroData, 6, startIndex, endIndex, numValues);
  // jsonString += ",\"my\":";
  // jsonString += serializeRawArray(accelGyroData, 7, startIndex, endIndex, numValues);
  // jsonString += ",\"mz\":";
  // jsonString += serializeRawArray(accelGyroData, 8, startIndex, endIndex, numValues);
  jsonString += ",\"sensor_id\":1";
  jsonString += "}]";

  // Close data object and JSON
  jsonString += "}}";

  return jsonString;
}

// Helper function to serialize raw integer arrays for a specific range
String serializeRawArray(int16_t* data, int offset, int startIndex, int endIndex, int numValues) {
  String arrayString = "[";
  for (int i = startIndex; i < endIndex; i++) {
    arrayString += String(data[i * numValues + offset]);  // Add raw integer value
    if (i < endIndex - 1) {
      arrayString += ",";
    }
  }
  arrayString += "]";
  return arrayString;
}

void sendDataToServer() {

  int totalBatches = numSamples / batchSize;
  for (int batchIndex = 0; batchIndex < totalBatches; batchIndex++) {
    int startIndex = batchIndex * batchSize;
    int endIndex = startIndex + batchSize;

    // Generate the JSON string for the current batch
    String jsonString = createJsonString(formattedDate, startIndex, endIndex);

    // Print the size of the JSON string
    SERIAL_PRINT("Size of JSON string: ");
    SERIAL_PRINT(jsonString.length());
    SERIAL_PRINT_LN(" bytes");

    // Print the JSON string
    SERIAL_PRINT_LN("Generated JSON String:");
    SERIAL_PRINT_LN(jsonString);

    // Send the JSON data to the server
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");
    // http.addHeader("User-Agent", "semIOE/2024.7");

    int httpResponseCode = http.POST(jsonString);

    if (httpResponseCode > 0) {
      String response = http.getString();
      SERIAL_PRINT_LN("HTTP Response Code: " + String(httpResponseCode));
      SERIAL_PRINT_LN("Server Response: " + response);
    } else {
      SERIAL_PRINT_LN("Error sending POST: " + String(httpResponseCode));
    }

    http.end();
  }
}

void mpuData() {
  int dataIndex = 0;
  int val = 0;
  timeClient.update();
  delay(500);
  formattedDate = timeClient.getFormattedDate();

  unsigned long previousMicros = micros();  // Initialize the previous time
  while (dataIndex < numSamples * numValues) {

    unsigned long currentMicros = micros();
    if (currentMicros - previousMicros >= 500) {
      previousMicros = currentMicros;  // Update the previous time

      xyzFloat accel = myMPU9250.getAccRawValues();
      xyzFloat gyro = myMPU9250.getGyrRawValues();
      // xyzFloat mag = myMPU9250.getMagValues();  // Read magnetometer data

      accelGyroData[dataIndex++] = accel.x;
      accelGyroData[dataIndex++] = accel.y;
      accelGyroData[dataIndex++] = accel.z;
      accelGyroData[dataIndex++] = gyro.x;
      accelGyroData[dataIndex++] = gyro.y;
      accelGyroData[dataIndex++] = gyro.z;
      accelGyroData[dataIndex++] = analogRead(ctAnalogPin);

      // accelGyroData[dataIndex++] = mag.x;
      // accelGyroData[dataIndex++] = mag.y;
      // accelGyroData[dataIndex++] = mag.z;
    }
  }
  SERIAL_PRINT_LN("Data Collected");
  // batchId++;
}

float calculateRMS_New(int pin, int samples, unsigned long interval) {
  int dataIndex = 0;
  int rawValue = 0;

  unsigned long sumVal = 0; // Use unsigned long to avoid overflow
  unsigned long previousMicros = micros();  

  while (dataIndex < samples) {
      unsigned long currentMicros = micros();
      if (currentMicros - previousMicros >= interval) {  // Use "interval" instead of hardcoded 500
          previousMicros = currentMicros;  // Update the previous time
          
          rawValue = analogRead(pin);
          sampleCurrent[dataIndex++] = rawValue;  // Store raw value
          sumVal += (unsigned long)rawValue;  // Sum the values
      }
  }

  float meanValue = (float)sumVal / samples;  // Compute Mean
  // SERIAL_PRINT_LN(meanValue);
  unsigned long sumSquares = 0;

  // Compute sum of squares
  for (int i = 0; i < samples; i++) { 
      float deviation = sampleCurrent[i] - meanValue; 
      // SERIAL_PRINT_LN(deviation);
      sumSquares += deviation*deviation;
  }

  float rmsValue = sqrt((float)sumSquares / samples);  // Compute RMS

  return rmsValue;
}

void mpuInit() {
  if (!myMPU9250.init()) {
    SERIAL_PRINT_LN("MPU9250 does not respond");
  } else {
    SERIAL_PRINT_LN("MPU9250 is connected");
  }

  if (!myMPU9250.initMagnetometer()) {
    SERIAL_PRINT_LN("Magnetometer does not respond");
  } else {
    SERIAL_PRINT_LN("Magnetometer is connected");
  }

  SERIAL_PRINT_LN("Position your MPU9250 flat and don't move it - calibrating...");
  delay(1000);
  myMPU9250.autoOffsets();
  SERIAL_PRINT_LN("Done!");

  myMPU9250.enableGyrDLPF();
  myMPU9250.setGyrDLPF(MPU9250_DLPF_6);
  myMPU9250.setSampleRateDivider(5);
  myMPU9250.setGyrRange(MPU9250_GYRO_RANGE_250);
  myMPU9250.setAccRange(MPU9250_ACC_RANGE_2G);
  myMPU9250.enableAccDLPF(true);
  myMPU9250.setAccDLPF(MPU9250_DLPF_6);
  myMPU9250.setMagOpMode(AK8963_CONT_MODE_100HZ);
}

void setup() {
  uint8_t mac[6];
  Serial.begin(115200);

  mpuInit();
  pinMode(ctAnalogPin, INPUT);
  
  connectToWiFi();

  // Initialize a NTPClient to get time
  timeClient.begin();

  // Getting Mac Address
  WiFi.macAddress(mac);

  macAddress = String(mac[0], HEX) + ":" +
              String(mac[1], HEX) + ":" +
              String(mac[2], HEX) + ":" +
              String(mac[3], HEX) + ":" +
              String(mac[4], HEX) + ":" +
              String(mac[5], HEX);

  SERIAL_PRINT("Wi-Fi MAC: ");
  SERIAL_PRINT_LN(macAddress);

  delay(1000);
}

void loop() {
  unsigned long currentMillis = millis();

  connectToWiFi();

  // Calculate the RMS value over a period using raw values
  float rmsValue = calculateRMS_New(ctAnalogPin, ctNumSamples, ctSampleInterval);

  // Determine if the machine is on or off based on the RMS threshold
  if (rmsValue > ctThreshold) {
    currentMotorStatus = 1;
  } else {
    currentMotorStatus = 0;
  }

  // Print the RMS value for debugging
  SERIAL_PRINT("RMS Value: ");
  SERIAL_PRINT_LN(rmsValue);

  if (currentMotorStatus != previousMotorStatus) {
    if (currentMotorStatus == 1){
        SERIAL_PRINT_LN("Machine is ON");
      } else {
        SERIAL_PRINT_LN("Machine is Off");
    }
    mpuData();
    sendDataToServer();
    previousMotorStatus = currentMotorStatus; // Update the previous state
    sdPreviousMillis = millis();
  } else if (currentMillis - sdPreviousMillis >= sendDataTimerMS) {
      SERIAL_PRINT(sendDataTimerMS);
      SERIAL_PRINT_LN(" ms have passed!");
      mpuData();
      sendDataToServer();
      sdPreviousMillis = millis();
  }

  delay(100);
}

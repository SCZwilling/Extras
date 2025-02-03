#include "WiFi.h"
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <MPU9250_WE.h>
#include <Wire.h>
#define MPU9250_ADDR 0x68

MPU9250_WE myMPU9250 = MPU9250_WE(MPU9250_ADDR);
const char* ssid = "Zwilling_Labs";
const char* password = "will@1234";
const String serverURL = "https://twin.zwillinglabs.io/api/iot/data";

WiFiClientSecure secureClient;
HTTPClient http;

bool isConnected = false;

// Define a structure to hold the data
struct SensorData {
  float ax;
  float ay;
  float az;
  float gx;
  float gy;
  float gz;
  int cps;
  String sensor_id;
};

QueueHandle_t uartQueue = NULL;
TaskHandle_t readUARTTask_h = NULL;
TaskHandle_t sendHTTPPostTask_h = NULL;

void readUARTTask(void* parameter) {
  for (;;) {
    xyzFloat accel = myMPU9250.getGValues();
    xyzFloat gyro = myMPU9250.getGyrValues();
    Serial.printf("Accel: %f, %f, %f | Gyro: %f, %f, %f\n", accel.x, accel.y, accel.z, gyro.x, gyro.y, gyro.z); // Debug statement

    // Fill the structure with data
    SensorData data;
    data.ax = accel.x;
    data.ay = accel.y;
    data.az = accel.z;
    data.gx = gyro.x;
    data.gy = gyro.y;
    data.gz = gyro.z;          
    data.sensor_id = "95";
    xQueueSend(uartQueue, &data, portMAX_DELAY);
    delay(1000);
  }
}

void sendHTTPPostTask(void* parameter) {
  Serial.println("HTTP POST task started");  // Debug statement
  SensorData data;

  for (;;) {
    if (xQueueReceive(uartQueue, &data, portMAX_DELAY)) {
      checkWifi();

      if (WiFi.status() == WL_CONNECTED) {
        secureClient.setInsecure();  // Uncomment if skipping certificate verification
        http.begin(secureClient, serverURL);  // HTTPS URL
        http.addHeader("Content-Type", "application/json");

        // Create JSON payload with required structure
        String jsonData = "{";
        jsonData += "\"mac_address\":\"00:1A:2B:3C:4D:5E\",";
        jsonData += "\"data\":{\"vibration\":[{";
        jsonData += "\"ax\":" + String(data.ax, 2) + ",";
        jsonData += "\"ay\":" + String(data.ay, 2) + ",";
        jsonData += "\"az\":" + String(data.az, 2) + ",";
        jsonData += "\"gx\":" + String(data.gx, 2) + ",";
        jsonData += "\"gy\":" + String(data.gy, 2) + ",";
        jsonData += "\"gz\":" + String(data.gz, 2) + ",";
        jsonData += "\"sensor_id\":\"" + data.sensor_id + "\"";
        jsonData += "}]}";
        jsonData += "}";

        int httpResponseCode = http.POST(jsonData);

        if (httpResponseCode > 0) {
          String response = http.getString();
          Serial.println("Response:");
          Serial.println(response);
        } else {
          Serial.print("Error on sending POST: ");
          Serial.println(httpResponseCode);
        }

        http.end();  // Close connection
      } else {
        Serial.println("WiFi not connected");
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  if(!myMPU9250.init()){
    Serial.println("MPU9250 does not respond");
  }
  else{
    Serial.println("MPU9250 is connected");
  }

  init_wifi(); // Initialize WiFi connection
  
  myMPU9250.autoOffsets();
  myMPU9250.enableGyrDLPF();
  myMPU9250.setGyrDLPF(MPU9250_DLPF_6);
  myMPU9250.setSampleRateDivider(5);
  myMPU9250.setGyrRange(MPU9250_GYRO_RANGE_250);
  myMPU9250.setAccRange(MPU9250_ACC_RANGE_2G);
  myMPU9250.enableAccDLPF(true);
  myMPU9250.setAccDLPF(MPU9250_DLPF_6);
  myMPU9250.setMagOpMode(AK8963_CONT_MODE_100HZ);

  // Queue for sending data between tasks
  uartQueue = xQueueCreate(10, sizeof(SensorData));
  if (uartQueue == nullptr) Serial.println("Queue Failed to be created");

  xTaskCreatePinnedToCore(
    readUARTTask,     // Function to be called
    "Read UART",      // Name of the task
    4096,             // Stack size (bytes)
    NULL,             // Parameter to pass
    1,                // Task priority
    &readUARTTask_h,  // Task handle
    0                 // Run on core 0
  );

  xTaskCreatePinnedToCore(
    sendHTTPPostTask,     // Function to be called
    "Send HTTP Post",     // Name of the task
    4096,                 // Stack size (bytes)
    NULL,                 // Parameter to pass
    1,                    // Task priority
    &sendHTTPPostTask_h,  // Task handle
    1                     // Run on core 1
  );
}

void loop() {
  // Empty loop
  delay(1000);
}

void init_wifi() {
  WiFi.mode(WIFI_STA);
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print("."); // Print dots while waiting to connect
  }
  Serial.println("\nWiFi connected");
}

void checkWifi() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, attempting to reconnect...");
    WiFi.reconnect();
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print("."); // Print dots while reconnecting
    }
    Serial.println("\nWiFi reconnected");
  }
}

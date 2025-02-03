#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <WiFi.h>
#include <WebSocketsClient.h>

static const int ledPin = 2;
static const char* ssid = "NCAIR IOT";
static const char* password = "Asim@123Tewari";
static const String targetMac = "d1:d6:24:02:61:2e";

BLEScan* pBLEScan;
static BLERemoteCharacteristic* pTPVCharacteristic;
static BLEAdvertisedDevice* myDevice;
WebSocketsClient webSocket;

static BLEUUID SERVICE_UUID("12345678-1234-5678-1234-56789abcdef0");
static BLEUUID CHAR_UUID("abcdef01-1234-5678-1234-56789abcdef1");

bool connected = false;
bool doConnect = false;

void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      connected = false;
      Serial.printf("[WSc] Disconnected!\n");
      break;
    case WStype_CONNECTED:
      connected = true;
      Serial.printf("[WSc] Connected to url: %s\n", payload);
      webSocket.sendTXT("Connected");
      break;
  }
}

class MyClientCallback : public BLEClientCallbacks {
  void onConnect(BLEClient* pclient) { connected = true; }
  void onDisconnect(BLEClient* pclient) {
    connected = false;
    Serial.println("Disconnected from BLE server");
  }
};

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    Serial.printf("Advertised Device: %s \n", advertisedDevice.toString().c_str());
    if (advertisedDevice.getAddress().toString() == targetMac) {
      Serial.print("Found BLE Advertised Device: ");
      Serial.println(advertisedDevice.toString().c_str());
      BLEDevice::getScan()->stop();
      myDevice = new BLEAdvertisedDevice(advertisedDevice);
      doConnect = true;
    }
  }
};

bool connectToServer() {
  Serial.print("Connecting to BLE Server: ");
  Serial.println(myDevice->getAddress().toString().c_str());

  BLEClient* pClient = BLEDevice::createClient();
  pClient->setClientCallbacks(new MyClientCallback());

  if (!pClient->connect(myDevice)) {
    Serial.println("Failed to connect to server. Reconnecting...");
    delay(1000);
    return false;
  }
  Serial.println("Connected to server.");

  BLERemoteService* pRemoteService = pClient->getService(SERVICE_UUID);
  if (!pRemoteService) {
    Serial.print("Failed to find service UUID: ");
    Serial.println(SERVICE_UUID.toString().c_str());
    pClient->disconnect();
    return false;
  }
  Serial.println("Found service.");

  pTPVCharacteristic = pRemoteService->getCharacteristic(CHAR_UUID);
  if (!pTPVCharacteristic) {
    Serial.print("Failed to find characteristic UUID: ");
    Serial.println(CHAR_UUID.toString().c_str());
    pClient->disconnect();
    return false;
  }
  Serial.println("Found characteristic.");

  return true;
}

void readCharacteristicValue() {
  if (pTPVCharacteristic->canRead()) {
    String value = pTPVCharacteristic->readValue();
    Serial.print("Characteristic value: ");
    for (char c : value) {
      Serial.print(c, HEX);
      Serial.print(" ");
    }
    Serial.println();
    
    // Send the entire value over WebSocket
    if (connected) {
      webSocket.sendTXT(value);
    }
  } else {
    Serial.println("Failed to read characteristic value!");
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(1349);
  pBLEScan->setWindow(449);
  pBLEScan->start(0, false);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  webSocket.begin("192.168.0.139",12345, "/");
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  if (doConnect) {
    if (connectToServer()) {
      Serial.println("Connected to BLE Server");
    }
    doConnect = false;
  }

  if (connected) {
    readCharacteristicValue();
    delay(1000);
    digitalWrite(ledPin, HIGH);
    delay(500);
    digitalWrite(ledPin, LOW);
    delay(500);
  }

  webSocket.loop(); // Keep WebSocket alive
}

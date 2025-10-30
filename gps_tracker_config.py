#!/usr/bin/env python3
"""
TruckTrace GPS Tracker Configuration Tool
Helps configure ESP32 GPS trackers for the TruckTrace system
"""

import json
import requests
import time
from datetime import datetime

class GPSTrackerConfig:
    def __init__(self, server_url="http://192.168.29.238:8080"):
        self.server_url = server_url
        self.api_base = f"{server_url}/api"
        
    def test_server_connection(self):
        """Test connection to TruckTrace server"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server connection successful")
                return True
            else:
                print(f"❌ Server returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Server connection failed: {e}")
            return False
    
    def register_tracker(self, hardware_id, vehicle_name=None):
        """Register a new GPS tracker with the system"""
        try:
            data = {
                "hardware_id": hardware_id,
                "vehicle_name": vehicle_name or f"GPS Tracker {hardware_id}",
                "latitude": 40.7589,  # Default NYC coordinates for testing
                "longitude": -73.9851,
                "speed_kph": 0,
                "heading_deg": 0,
                "odometer_km": 0,
                "satellites": 8,
                "hdop": 1.2,
                "source": "esp32_gps_enhanced"
            }
            
            response = requests.post(f"{self.api_base}/hardware/gps", json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Tracker registered successfully")
                print(f"   Hardware ID: {hardware_id}")
                print(f"   Vehicle ID: {result.get('vehicle_id')}")
                print(f"   Signal Quality: {result.get('signal_quality')}")
                return result
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Registration error: {e}")
            return None
    
    def send_test_data(self, hardware_id, count=5):
        """Send test GPS data to verify tracker is working"""
        print(f"📡 Sending {count} test GPS updates...")
        
        # NYC area coordinates for testing
        test_coordinates = [
            (40.7589, -73.9851),  # Times Square
            (40.7505, -73.9934),  # Empire State Building
            (40.7614, -73.9776),  # Central Park
            (40.7282, -74.0776),  # Brooklyn Bridge
            (40.7831, -73.9712),  # Upper East Side
        ]
        
        for i in range(count):
            lat, lon = test_coordinates[i % len(test_coordinates)]
            
            # Add some variation to coordinates
            lat += (i * 0.001)
            lon += (i * 0.0005)
            
            data = {
                "hardware_id": hardware_id,
                "latitude": lat,
                "longitude": lon,
                "speed_kph": 30 + (i * 5),
                "heading_deg": (i * 45) % 360,
                "odometer_km": i * 2.5,
                "satellites": 8 + (i % 3),
                "hdop": 1.2 + (i * 0.1),
                "source": "esp32_gps_enhanced"
            }
            
            try:
                response = requests.post(f"{self.api_base}/locations", json=data, timeout=10)
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ Update {i+1}/{count} sent successfully")
                else:
                    print(f"   ❌ Update {i+1}/{count} failed: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Update {i+1}/{count} error: {e}")
            
            time.sleep(2)  # Wait 2 seconds between updates
    
    def check_tracker_status(self, hardware_id=None):
        """Check the status of GPS trackers"""
        try:
            response = requests.get(f"{self.api_base}/hardware/status", timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                print("📊 GPS Tracker Status:")
                print(f"   Hardware Connected: {status.get('hardware_connected')}")
                print(f"   Recent Updates: {status.get('recent_updates')}")
                print(f"   Signal Quality: {status.get('signal_quality')}")
                print(f"   Last Update: {status.get('last_update')}")
                
                if status.get('gps_vehicles'):
                    print("\n🚛 GPS Vehicles:")
                    for vehicle in status['gps_vehicles']:
                        print(f"   • {vehicle['name']} ({vehicle['plate']})")
                        print(f"     Location: {vehicle['latitude']:.4f}, {vehicle['longitude']:.4f}")
                        print(f"     Speed: {vehicle['speed_kph']} km/h")
                        print(f"     Satellites: {vehicle['satellites']}")
                        print(f"     Last Update: {vehicle['recorded_at']}")
                        print()
                
                return status
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Status check error: {e}")
            return None
    
    def generate_arduino_code(self, hardware_id, wifi_ssid, wifi_password, server_ip="192.168.29.238"):
        """Generate Arduino code for ESP32 GPS tracker"""
        
        arduino_code = f'''
// TruckTrace GPS Tracker - Generated Configuration
// Hardware ID: {hardware_id}
// Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPS++.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "{wifi_ssid}";
const char* password = "{wifi_password}";

// Server Configuration
const char* serverUrl = "http://{server_ip}:8080/api/locations";
const String hardwareId = "{hardware_id}";

// GPS Configuration
#define GPS_RX 16
#define GPS_TX 17
HardwareSerial GPS_Serial(2);
TinyGPSPlus gps;

// Tracking Variables
double lastLat = 0.0, lastLon = 0.0;
double odometer_km = 0.0;
unsigned long lastPostTime = 0;
const unsigned long GPS_UPDATE_INTERVAL = 10000; // 10 seconds

void setup() {{
  Serial.begin(115200);
  GPS_Serial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  
  Serial.println("🚛 TruckTrace GPS Tracker Starting...");
  Serial.println("Hardware ID: {hardware_id}");
  
  connectToWiFi();
  Serial.println("✅ GPS Tracker Ready!");
}}

void loop() {{
  while (GPS_Serial.available()) {{
    if (gps.encode(GPS_Serial.read())) {{
      if (gps.location.isValid()) {{
        processGPSData();
      }}
    }}
  }}
  
  if (WiFi.status() != WL_CONNECTED) {{
    connectToWiFi();
  }}
  
  delay(100);
}}

void connectToWiFi() {{
  WiFi.begin(ssid, password);
  Serial.print("📶 Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {{
    delay(500);
    Serial.print(".");
  }}
  
  Serial.println();
  Serial.println("✅ WiFi Connected!");
  Serial.print("📍 IP Address: ");
  Serial.println(WiFi.localIP());
}}

void processGPSData() {{
  if (millis() - lastPostTime > GPS_UPDATE_INTERVAL) {{
    double lat = gps.location.lat();
    double lon = gps.location.lng();
    double speed_kph = gps.speed.isValid() ? gps.speed.kmph() : 0.0;
    double heading = gps.course.isValid() ? gps.course.deg() : 0.0;
    int satellites = gps.satellites.isValid() ? gps.satellites.value() : 0;
    double hdop = gps.hdop.isValid() ? gps.hdop.hdop() : 99.99;
    
    if (lastLat != 0.0 && lastLon != 0.0) {{
      double dist_m = TinyGPSPlus::distanceBetween(lastLat, lastLon, lat, lon);
      if (dist_m > 5.0) {{
        odometer_km += dist_m / 1000.0;
      }}
    }}
    
    lastLat = lat;
    lastLon = lon;
    
    sendGPSData(lat, lon, speed_kph, heading, satellites, hdop);
    lastPostTime = millis();
  }}
}}

void sendGPSData(double lat, double lon, double speed, double heading, int sats, double hdop) {{
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  DynamicJsonDocument doc(1024);
  doc["hardware_id"] = hardwareId;
  doc["latitude"] = lat;
  doc["longitude"] = lon;
  doc["speed_kph"] = speed;
  doc["heading_deg"] = heading;
  doc["odometer_km"] = odometer_km;
  doc["satellites"] = sats;
  doc["hdop"] = hdop;
  doc["source"] = "esp32_gps_enhanced";
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  Serial.println("📡 Sending: " + jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {{
    Serial.println("✅ Response: " + String(httpResponseCode));
  }} else {{
    Serial.println("❌ Error: " + String(httpResponseCode));
  }}
  
  http.end();
}}
'''
        
        filename = f"trucktrace_gps_{hardware_id}.ino"
        with open(filename, 'w') as f:
            f.write(arduino_code)
        
        print(f"✅ Arduino code generated: {filename}")
        return filename

def main():
    print("🚛 TruckTrace GPS Tracker Configuration Tool")
    print("=" * 50)
    
    config = GPSTrackerConfig()
    
    # Test server connection
    if not config.test_server_connection():
        print("Please ensure TruckTrace server is running and accessible")
        return
    
    while True:
        print("\nOptions:")
        print("1. Register new GPS tracker")
        print("2. Send test data")
        print("3. Check tracker status")
        print("4. Generate Arduino code")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            hardware_id = input("Enter hardware ID (e.g., ESP32-001): ").strip()
            vehicle_name = input("Enter vehicle name (optional): ").strip()
            config.register_tracker(hardware_id, vehicle_name or None)
            
        elif choice == "2":
            hardware_id = input("Enter hardware ID: ").strip()
            count = input("Number of test updates (default 5): ").strip()
            count = int(count) if count.isdigit() else 5
            config.send_test_data(hardware_id, count)
            
        elif choice == "3":
            config.check_tracker_status()
            
        elif choice == "4":
            hardware_id = input("Enter hardware ID: ").strip()
            wifi_ssid = input("Enter WiFi SSID: ").strip()
            wifi_password = input("Enter WiFi password: ").strip()
            server_ip = input("Enter server IP (default 192.168.29.238): ").strip()
            server_ip = server_ip or "192.168.29.238"
            config.generate_arduino_code(hardware_id, wifi_ssid, wifi_password, server_ip)
            
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
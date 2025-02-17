# ESP8266 MQTT to FastAPI

This project demonstrates how an ESP8266 device sends random numbers over MQTT to a FastAPI server, which then plots the last 10 received values on a graph.

## Features
- ESP8266 generates and sends random numbers to an MQTT broker.
- FastAPI subscribes to the MQTT topic and receives the data.
- The server updates a real-time graph displaying the last 10 received values.

## Components Used
- **ESP8266**: Publishes random numbers to an MQTT broker.
- **MQTT Broker**: Handles communication between ESP8266 and FastAPI.
- **FastAPI**: Receives data and updates the graph.
- **Matplotlib**: Renders the graph for visualization.

## Installation

### 1. Set up FastAPI Server
```bash
pip install fastapi uvicorn paho-mqtt matplotlib
```

### 2. Run the FastAPI Server
```bash
uvicorn main:app --reload
```

### 3. Configure ESP8266 (Arduino IDE)
Ensure the ESP8266 is programmed to send random numbers via MQTT.

### 4. Run the MQTT Broker
Use an MQTT broker locally or a cloud-based service.


## Usage
1. Power up the ESP8266 and ensure it's connected to Wi-Fi.
2. Start the FastAPI server.
3. Check the real-time graph at `http://127.0.0.1:8000/graph`.
4. Monitor received data via MQTT.

## Example Data Flow
1. ESP8266 publishes `random_number` to `mqtt/topic/random`.
2. FastAPI subscribes and stores the last 10 received numbers.
3. `/graph` displays the real-time updates.

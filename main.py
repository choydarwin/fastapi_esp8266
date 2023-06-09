from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import HTMLResponse
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import io
import base64
import uvicorn
import asyncio
from datetime import datetime

app = FastAPI()

# Define global variables for the plot data
max_data_points = 10  # Maximum number of data points to display
y_data = []
timestamps = []

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("random_number")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    # Convert the payload to a float
    value = float(msg.payload)

    # Get the current timestamp
    timestamp = datetime.now()

    # Update the plot data
    y_data.append(value)
    timestamps.append(timestamp)

    # Keep only the last max_data_points data points
    if len(y_data) > max_data_points:
        y_data.pop(0)
        timestamps.pop(0)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.0.103", 1883, 60)

websocket_connections = set()

async def update_plot_data():
    while True:
        if len(y_data) > 0:
            x_data = timestamps[-len(y_data):]  # Use the timestamps as x-axis values

            plt.figure(figsize=(30, 20))  # Increase the figure size

            # Create a plot with all the data points
            plt.plot(x_data, y_data, marker='o')
            plt.xlabel("Hora de la muestra", fontsize=30)  # Increase the font size of x-axis label
            plt.ylabel("Temperatura", fontsize=30)  # Increase the font size of y-axis label
            plt.tick_params(axis="both", which="major", labelsize=50)  # Increase the font size of axis ticks

            # Configure the x-axis to display dates nicely
            plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
            plt.gcf().autofmt_xdate()  # Rotate and align the x-axis tick labels

            # Save the plot to a BytesIO buffer
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)

            # Encode the plot as base64
            plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            # Send the updated plot data to all connected WebSocket clients
            for websocket in websocket_connections.copy():
                try:
                    await websocket.send_text(plot_base64)  # Send the plot data as Base64-encoded string
                except WebSocketDisconnect:
                    # Remove the WebSocket connection from the set of connections
                    websocket_connections.remove(websocket)

            # Clear the plot
            plt.clf()
            plt.close()

        # Sleep for a while before updating again
        await asyncio.sleep(1)  # Adjust the sleep duration as needed

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Add the WebSocket connection to the set of connections
    websocket_connections.add(websocket)

    try:
        while True:
            # Keep the WebSocket connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Remove the WebSocket connection from the set of connections
        websocket_connections.remove(websocket)

@app.get("/plot")
async def plot_data(background_tasks: BackgroundTasks):
    # Schedule the background task to update the plot data periodically
    background_tasks.add_task(update_plot_data)

    # Read the HTML content from the file
    with open("index.html", "r") as html_file:
        html_content = html_file.read()

    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    client.loop_start()
    uvicorn.run(app, host="0.0.0.0", port=8000)

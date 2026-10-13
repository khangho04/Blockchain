import json
import paho.mqtt.client as mqtt

from .processor import process_energy_data


MQTT_BROKER = "localhost"
MQTT_PORT = 1883

MQTT_TOPIC = "energy/house/+"


def on_connect(client, userdata, flags, reason_code, properties):

    if reason_code == 0:

        print("Connected to MQTT Broker")

        client.subscribe(MQTT_TOPIC)

        print(
            f"Subscribed to: {MQTT_TOPIC}"
        )

    else:

        print(
            f"Connection failed. "
            f"Reason code: {reason_code}"
        )


def on_message(client, userdata, message):

    try:

        
        # 1. Decode MQTT message
        payload = message.payload.decode()

        print("\nReceived MQTT message:")
        print(payload)

        # 2. Convert JSON → Python dictionary
        data = json.loads(payload)

        # 3. Send data to processor
        process_energy_data(data)

    except json.JSONDecodeError:

        print("ERROR: Invalid JSON")

    except Exception as e:

        print(
            f"ERROR processing message: {e}"
        )


def main():

    # Paho MQTT Callback API v2
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    # Register callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to Mosquitto
    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    print("Backend is running...")
    print("Waiting for energy data...")

    # Keep MQTT connection running
    client.loop_forever()


if __name__ == "__main__":
    main()


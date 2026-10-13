import json
import time

import paho.mqtt.client as mqtt

from iot_code.Simulator.energy_simulator import (
    simulate_all_houses
)


MQTT_BROKER = "localhost"
MQTT_PORT = 1883

MQTT_TOPIC = "energy/house"


def connect_mqtt():

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    print("Connected to MQTT Broker")

    return client


def prepare_message(data):

    return {
        "hour": data["hour"],
        "house_id": data["house_id"],
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "solar_irradiance": data["solar_irradiance"],
        "production_kwh": data["production_kwh"],
        "consumption_kwh": data["consumption_kwh"],
        "surplus_kwh": data["surplus_kwh"],
        "status": data["status"]
    }


def publish_energy_data(client, data):

    house_id = data["house_id"]

    topic = f"{MQTT_TOPIC}/{house_id}"

    message_data = prepare_message(data)

    message = json.dumps(
        message_data
    )

    result = client.publish(
        topic,
        message
    )

    if result.rc == mqtt.MQTT_ERR_SUCCESS:

        print(
            f"[MQTT] Published → "
            f"{topic}"
        )

        print(
            f"        Hour: {data['hour']} | "
            f"Temp: {data['temperature']} °C | "
            f"Humidity: {data['humidity']} % | "
            f"Irradiance: {data['solar_irradiance']} W/m²"
        )

        print(
            f"        Production: "
            f"{data['production_kwh']} kWh | "
            f"Consumption: "
            f"{data['consumption_kwh']} kWh"
        )

    else:

        print(
            f"[MQTT] Failed → "
            f"{topic}"
        )


def main():

    client = connect_mqtt()

    client.loop_start()

    all_data = simulate_all_houses()

    selected_data = [
        row
        for row in all_data
        if row["hour"] == 12
    ]

    for data in selected_data:

        publish_energy_data(
            client,
            data
        )

        time.sleep(0.5)

    time.sleep(1)

    client.loop_stop()

    client.disconnect()

    print("Disconnected from MQTT Broker")


if __name__ == "__main__":
    main()
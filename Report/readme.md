
# Pizza Shop Monitoring System – README

## Contents
- Versions
- WSL Setup
- Install Kafka
- Initial Kafka Setup
- Network Configuration
- Kafka Usage
- Database Setup
- Connection Keys
- Run Modules
- Notes

---

## Versions

- **OS**: Ubuntu 24 (WSL on Windows 11)
- **Python**: 3.11.7
- **Kafka**: 4.1.1
- **Java**: OpenJDK 11

---

## WSL Setup

Ensure WSL is installed and Ubuntu 24 is configured on Windows 11.

---

## Install Kafka

```bash
sudo apt install openjdk-11-jdk -y
wget https://downloads.apache.org/kafka/4.1.1/kafka_2.13-4.1.1.tgz
tar -xvf kafka_2.13-4.1.1.tgz
mv kafka_2.13-4.1.1 ~/kafka
````

---

## Initial Kafka Setup (First Time Only)

```bash
cd ~/kafka

# Generate cluster UUID
bin/kafka-storage.sh random-uuid

# Format storage (replace YOUR_UUID_HERE)
bin/kafka-storage.sh format -t YOUR_UUID_HERE -c config/server.properties --standalone

# Create test topic
bin/kafka-topics.sh --create \
  --topic test-topic \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

---

## Network Configuration

### Get WSL IP Address

```bash
ip addr show eth0
```

### Modify `config/server.properties`

```properties
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://:9093

# Listener used for communication between brokers
inter.broker.listener.name=PLAINTEXT

# Advertised listeners (replace with your WSL IP)
advertised.listeners=PLAINTEXT://172.20.197.213:9092,CONTROLLER://172.20.197.213:9093
```

### Increase Maximum Message Size (for image frames)

```properties
message.max.bytes=52428800        # 50 MB
replica.fetch.max.bytes=52428800  # 50 MB
```

---

## Kafka Usage

### Start Kafka Server

```bash
cd ~/kafka
bin/kafka-server-start.sh config/server.properties
```

### Consume Frames Topic (Debugging)

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server 127.0.0.1:9092 \
  --topic frames \
  --from-beginning
```

---

## Database Setup

* Create a MySQL database using **XAMPP**
* Create a table named `store_violations`
* Table fields (all stored as strings):

  * `warned_frame_ingred`
  * `time_stamp_ingred`
  * `warned_frame_pizza`

---

## Connection Keys

* Update database credentials if XAMPP is not using default settings
* Update WSL IP address in all modules
* Store all configuration values in a shared `keys` file per module:

  * Database host, username, password
  * Kafka broker IP
  * Any additional service keys

---

## Run Modules

To ensure correct execution and avoid frame loss, run the modules in the following order.
(In production, this is typically handled using Docker or orchestration tools.)

### Recommended Execution Order

1. **Module_0_camera**

   * Starts the video stream using FastAPI

2. **Module_2_frame_streamer**

   * Run early to avoid losing any frames

3. **Module_1_frame_reader**

   * Reads frames and publishes them to Kafka topics

4. **Module_4_backend**

   * Backend service to display and store detection results

5. **Module_3_detect**

   * Core detection and tracking logic

6. **Module_5_front**

   * Main frontend web interface


# 🛡️ S.I.D.E. – SCADA Intrusion Detection Environment

**S.I.D.E.** (SCADA Intrusion Detection Environment) is a **next-generation Intrusion Detection System (IDS)** designed for industrial control networks (ICS/SCADA).

It **monitors SCADA devices**, **detects network anomalies**, and provides **real-time alerts**, ensuring your industrial network remains **secure, resilient, and operational**.

> **Visual Diagram:**
> The complete architecture of S.I.D.E. is available in both **Excalidraw (.excalidraw)** and **PNG** formats for an interactive, detailed overview.
>
> The `.excalidraw` file can be opened directly in **Visual Studio Code** using the [**Excalidraw Editor extension**](https://marketplace.visualstudio.com/items?itemName=pomdtr.excalidraw-editor).

---



## 🗂️ Repository Structure

### `side-sniff/` – 🕵️‍♂️ Network IDS

Captures **industrial network packets** and identifies potential threats in real-time.  

**Features:**

- Supports **MODBUS/TCP, SNAP7, OPC-UA**.
- Flexible detection methods:
  - **Rule Matching** ✅
  - **Z-Score** (statistical anomaly detection) 📊
  - **Machine Learning-based detection** 🤖
- Export captured data to **downstream modules** (`side-ml-models`, `side-api-backend`).

---

### `side-device-discovery/` – 🔍 Device Discovery & Management

Automates **SCADA device detection** and event monitoring.  

**Features:**

- Detects active device events and protocols.
- Maintains **live network inventory**.
- Feeds **real-time data** to `side-api-backend` for visualization.

---

### `side-api-backend/` – ⚡ Backend & REST API

Central hub for all network data, enabling **queries, analytics, and alerts**.  

**Features:**

- Aggregates data from `side-sniff` & `side-device-discovery`.
- Stores traffic & event data in a **Neo4J graph database**.
- Serves **real-time API endpoints** for dashboards and integrations.

---

### `side-frontends/` – 🎨 Interactive Dashboard

Visualize your SCADA network like a pro hacker.  

**Features:**

- Interactive **device & traffic maps**.
- **Real-time alerts** & anomaly indicators.
- Filter by device type, protocol, or network segment.
- Built with **Next.js**, fully extensible.

---

### `side-ml-models/` – 🤖 Machine Learning Modules

Leverages **AI to detect unusual activity** in your network.  

**Features:**

- Processes **PCAP files** from `side-sniff`.
- Trains **Isolation Forest models** to identify abnormal behaviors.
- Generates **anomaly scores** & triggers **automated alerts**.

---

### `test/` – 🧪 Simulation & PenTesting Playground

Test your IDS in a **safe, simulated environment**.  

Supports:

- **MODBUS** – Simulated Modbus/TCP devices.
- **SNAP7** – Siemens PLC simulations.
- **OPC-UA** – Simulated OPC-UA servers.

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/SIDE.git
cd SIDE
```

### 2️⃣ Install Dependencies

- Python 3.12.10 → `pip install -r requirements.txt`
- Node.js LTS → for frontend
- RabbitMQ → for event messaging
- Neo4J → run with Docker:

```bash
docker run -d --name neo4-scada --restart always \
  --publish 7474:7474 --publish 7687:7687 \
  --env NEO4J_AUTH=neo4j/scada_devices neo4j:latest
```

### 3️⃣ Run the System

1. Start `side-sniff` to capture packets 🕵️‍♂️
2. Start `side-device-discovery` to detect devices 🔍
3. Start `side-api-backend` to serve APIs ⚡
4. Open `side-frontends` for real-time visualization 🎨

### 4️⃣ Test with Simulated Networks

Run scripts in `test/` to safely validate detection for:

- MODBUS ✅
- SNAP7 ✅
- OPC-UA ✅

---

## 🤝 Contributing

We welcome **contributors, pen-testers, and security enthusiasts**!

- Follow the modular architecture.
- Test new features with the provided simulation datasets.
- Help improve detection accuracy and extend protocol support.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

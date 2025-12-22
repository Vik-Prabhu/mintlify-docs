# Smart Fault Detector - [Github](https://github.com/Addwaaait/Smart-Fault-Detector)


## 📘 Project Documentation & Deployment

### 🌐 Documentation (Mintlify)
This project uses **Mintlify** to host clean, modern documentation.

- Built using MDX
- Supports images, code blocks, and downloadable assets
- Automatically deployed on every update

📖 **Docs URL:**  https://teamrobomanipal-3a657712.mintlify.app/Introduction
````
To run docs locally:
npm install
mintlify dev
````

To deploy docs:

```
mintlify publish
```

---

### 🚀 Backend Deployment (Render + Flask)

The backend is a **Flask + Socket.IO** server deployed on **Render**.

#### Why Render?

* Free tier support
* Simple GitHub integration
* Works well with Flask APIs
* Public endpoint accessible by ESP devices

#### Tech Stack

* Python
* Flask
* Flask-SocketIO
* Eventlet
* Render Web Service

#### Deployment Flow

1. Push code to GitHub
2. Create a **Web Service** on Render
3. Render installs dependencies from `requirements.txt`
4. App runs on a public HTTPS URL

#### **Backend URL:** [https://teamrobomanipal-3a657712.mintlify.app/Introduction](https://mintlify-docs-w26p.onrender.com


---

### 📡 ESP ↔ Server Communication

* ESP device sends data via HTTP / Socket.IO
* Flask server receives and processes data
* Real-time updates supported using WebSockets
* Designed for low-latency actuator/health monitoring

---

### 📂 Key Files

```text
.
├── docs.json             # Contains structured metadata for the project 
├── package-lock.json     # Auto-generated file that locks exact package versions installed via npm for mintlify
```
```
Dashboard_src
├── server.py              # Webserver UI
├── health_model.py        # Predictive Algorithm
├── requirements.txt       # Python dependencies
```

---

### 🛠️ requirements.txt

```txt
flask
flask-socketio
eventlet
```

---

### ✅ Status

* [x] Backend deployed on Render
* [x] Documentation live on Mintlify
* [x] ESP integration working
* [x] GitHub CI-ready

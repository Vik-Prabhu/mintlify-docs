from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO
import time

# Import health model
from health_model import calculate_health

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ================= HTML TEMPLATE (with JS fixed) =================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actuator Health Monitor</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
        .sidebar { width: 260px; background-color: #0d1117; border-right: 1px solid #21262d; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; }
        .nav-item { cursor: pointer; transition: all 0.2s; }
        .nav-active { background-color: #1f2937; color: white; border-left: 4px solid #3b82f6; }
        .hidden-section { display: none; }
        .value-red { color: #f85149; }
    </style>
</head>
<body class="flex min-h-screen">

    <aside class="sidebar flex flex-col p-6">
        <div class="flex items-center gap-3 mb-10">
            <div class="bg-blue-600 p-2 rounded-md"><i class="fas fa-tools text-white"></i></div>
            <span class="font-bold text-xl tracking-tight text-white">Fault Detector</span>
        </div>
        <nav class="space-y-2">
            <div id="btn-dash" onclick="showSection('dashboard')" class="nav-item nav-active p-3 rounded-lg flex items-center gap-3">
                <i class="fas fa-tachometer-alt"></i> Dashboard
            </div>
            <div id="btn-logs" onclick="showSection('logs')" class="nav-item p-3 rounded-lg flex items-center gap-3 text-gray-500 hover:bg-[#21262d]">
                <i class="fas fa-wave-square"></i> Data Logs
            </div>
        </nav>
    </aside>

    <main class="flex-1 flex flex-col">
        <header class="px-8 py-6 border-b border-[#21262d] flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-white">Industrial IoT Monitor</h1>
                <p class="text-xs text-gray-500 mt-1">ESP32-C3 System • <span id="time-display">--:--:--</span></p>
            </div>
            <div class="flex items-center gap-6 text-xs font-semibold">
                <div class="flex items-center gap-2">
                    <span class="text-gray-500">STATUS:</span>
                    <span id="conn-status" class="text-red-500 bg-red-500/10 px-2 py-1 rounded">Disconnected</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-gray-500">SAMPLES:</span>
                    <span id="readings-count" class="text-blue-400">0</span>
                </div>
            </div>
        </header>

        <div id="section-dashboard" class="p-8 space-y-10">
            <section>
                <h2 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 text-white">Mechanical Health</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl">
                    <div class="card p-6 border-l-4 border-blue-400">
                        <p class="text-gray-500 text-xs font-bold uppercase mb-1">Rotational Speed</p>
                        <div class="text-4xl font-light text-blue-400"><span id="rpm">--</span> <span class="text-lg text-gray-500">RPM</span></div>
                    </div>
                    <div class="card p-6 border-l-4 border-purple-500">
                        <p class="text-gray-500 text-xs font-bold uppercase mb-1">Vibration Intensity</p>
                        <div class="text-4xl font-light text-purple-400"><span id="vib">--</span> <span class="text-lg text-gray-500">g</span></div>
                    </div>
                </div>
            </section>

            <section>
                <h2 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4 text-white">Actuator Status</h2>
                <div id="actuator-grid" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <p class="text-gray-600">Waiting for Port Data...</p>
                </div>
            </section>
        </div>

        <div id="section-logs" class="p-8 hidden-section">
            <h2 class="text-xl font-bold mb-6 text-white text-center">Live Multi-Channel Power Logs</h2>
            <div class="grid grid-cols-1 gap-8">
                <div class="card p-6">
                    <h3 class="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest">3-Channel Voltage (V)</h3>
                    <div style="height: 250px;"><canvas id="voltageChart"></canvas></div>
                </div>
                <div class="card p-6">
                    <h3 class="text-xs font-bold text-gray-400 mb-4 uppercase tracking-widest">3-Channel Current (A)</h3>
                    <div style="height: 250px;"><canvas id="currentChart"></canvas></div>
                </div>
            </div>
        </div>
    </main>

    <script>
        const socket = io();
        let readingsCount = 0;
        let lastReceived = 0;
        const colors = ['#3b82f6', '#10b981', '#f59e0b']; // Actuator 1, 2, 3

        function showSection(section) {
            document.getElementById('section-dashboard').classList.toggle('hidden-section', section !== 'dashboard');
            document.getElementById('section-logs').classList.toggle('hidden-section', section !== 'logs');
            document.getElementById('btn-dash').classList.toggle('nav-active', section === 'dashboard');
            document.getElementById('btn-logs').classList.toggle('nav-active', section === 'logs');
        }

        // Chart Config
        function createChartConfig() {
            return {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        { label: 'Act. 1', borderColor: colors[0], data: [], tension: 0.3, pointRadius: 0 },
                        { label: 'Act. 2', borderColor: colors[1], data: [], tension: 0.3, pointRadius: 0 },
                        { label: 'Act. 3', borderColor: colors[2], data: [], tension: 0.3, pointRadius: 0 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#8b949e', font: { size: 10 } } } },
                    scales: {
                        y: { grid: { color: '#21262d' }, ticks: { color: '#8b949e' } },
                        x: { grid: { display: false }, ticks: { color: '#8b949e' } }
                    }
                }
            };
        }

        const voltChart = new Chart(document.getElementById('voltageChart'), createChartConfig());
        const currChart = new Chart(document.getElementById('currentChart'), createChartConfig());

        function updateTime() {
            const now = Date.now();
            document.getElementById('time-display').innerText = new Date().toLocaleTimeString();
            const status = document.getElementById('conn-status');
            if (now - lastReceived > 5000) {
                status.innerText = "Disconnected";
                status.className = "text-red-500 bg-red-500/10 px-2 py-1 rounded";
            } else {
                status.innerText = "Connected";
                status.className = "text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded";
            }
        }
        setInterval(updateTime, 1000);

        socket.on('sensor_update', (data) => {
            lastReceived = Date.now();
            readingsCount++;
            document.getElementById('readings-count').innerText = readingsCount;
            
            // Update RPM and Vibration (replaces Temp/Hum)
            document.getElementById('rpm').innerText = data.rpm || 0;
            document.getElementById('vib').innerText = data.vibration || 0;

            const timeLabel = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            [voltChart, currChart].forEach(c => {
                if(c.data.labels.length > 25) { 
                    c.data.labels.shift(); 
                    c.data.datasets.forEach(ds => ds.data.shift());
                }
                c.data.labels.push(timeLabel);
            });

            // push new values
            for(let i=0; i<3; i++) {
                const p = data.ports[i] || { voltage: 0, current: 0 };
                voltChart.data.datasets[i].data.push(p.voltage || 0);
                currChart.data.datasets[i].data.push(p.current || 0);
            }
            voltChart.update('none');
            currChart.update('none');

            const grid = document.getElementById('actuator-grid');
            grid.innerHTML = '';
            data.ports.slice(0, 3).forEach((port, idx) => {
                // use server-provided health if available, otherwise estimate 100
                const health = (typeof port.health !== 'undefined') ? port.health : 100.0;

                // fault decision is now ML-driven (health threshold)
                const isFault = (health < 40);

                grid.innerHTML += `
                    <div class="card p-6 border-t-2" style="border-top-color: ${colors[idx]}">
                        <div class="flex justify-between items-center mb-4 text-white">
                            <h3 class="font-bold text-sm">Actuator ${port.port}</h3>
                            <span class="text-[9px] ${isFault ? 'text-red-500 bg-red-500/10' : 'text-emerald-500 bg-emerald-500/10'} px-2 py-1 rounded font-bold uppercase">
                                ${isFault ? 'MAINTENANCE' : 'HEALTHY'}
                            </span>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <div class="bg-[#0d1117] p-3 rounded-lg border border-gray-800">
                                <p class="text-[9px] text-gray-500 mb-1 font-bold tracking-widest">VOLTAGE</p>
                                <div class="text-xl font-mono text-amber-500 font-bold">${(port.voltage||0).toFixed(1)}V</div>
                            </div>
                            <div class="bg-[#0d1117] p-3 rounded-lg border border-gray-800">
                                <p class="text-[9px] text-gray-500 mb-1 font-bold tracking-widest">CURRENT</p>
                                <div class="text-xl font-mono text-blue-400 font-bold">${(port.current||0).toFixed(2)}A</div>
                            </div>

                            <!-- HEALTH (span across both columns) -->
                            <div class="col-span-2 bg-[#0d1117] p-3 rounded-lg border border-gray-800 mt-2">
                                <p class="text-[9px] text-gray-500 mb-1 font-bold tracking-widest">HEALTH</p>
                                <div class="text-2xl font-bold ${
                                    health < 40 ? 'text-red-500' :
                                    health < 70 ? 'text-yellow-400' :
                                    'text-emerald-400'
                                }">
                                    ${health.toFixed(1)}%
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }); /* <--- IMPORTANT: closing the socket.on handler */

    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/update', methods=['POST'])
def update():
    data = request.json

    # quick sanity: ensure expected structure
    if data is None:
        return jsonify({"error": "no json body"}), 400

    rpm = data.get("rpm", 0)
    vibration = data.get("vibration", 0)

    # --- Simple trend placeholders (can be upgraded later) ---
    current_trend = 0.0
    vibration_trend = 0.0

    # Calculate health for each actuator
    for port in data.get("ports", []):
        current = port.get("current", 0.0)
        voltage = port.get("voltage", 0.0)

        health = calculate_health(
            current=current,
            voltage=voltage,
            vibration=vibration,
            current_trend=current_trend,
            vibration_trend=vibration_trend
        )

        # Attach health to actuator JSON
        port["health"] = round(health, 1)

    # Optional debug print (uncomment while debugging)
    # print("Emitting:", data)

    socketio.emit('sensor_update', data)
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

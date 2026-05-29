const API_BASE_URL = "https://postureio-backend.onrender.com";

const elements = {
  apiKey: document.getElementById("apiKey"),
  saveKeyBtn: document.getElementById("saveKeyBtn"),
  keyStatus: document.getElementById("keyStatus"),
  keyPanelStatus: document.getElementById("keyPanelStatus"),
  apiKeyPanel: document.getElementById("apiKeyPanel"),
  refreshBtn: document.getElementById("refreshBtn"),
  loadAllBtn: document.getElementById("loadAllBtn"),
  backendCard: document.getElementById("backendCard"),
  currentPostureCard: document.getElementById("currentPostureCard"),
  riskCard: document.getElementById("riskCard"),
  backendStatus: document.getElementById("backendStatus"),
  backendMessage: document.getElementById("backendMessage"),
  currentPosture: document.getElementById("currentPosture"),
  currentPostureMeta: document.getElementById("currentPostureMeta"),
  riskLevel: document.getElementById("riskLevel"),
  riskMessage: document.getElementById("riskMessage"),
  aiSource: document.getElementById("aiSource"),
  aiAdvice: document.getElementById("aiAdvice"),
  totalReadings: document.getElementById("totalReadings"),
  badPosture: document.getElementById("badPosture"),
  goodPosture: document.getElementById("goodPosture"),
  mostCommon: document.getElementById("mostCommon"),
  historyTable: document.getElementById("historyTable"),
  historyHelper: document.getElementById("historyHelper")
};

let historyLimit = 10;

function getApiKey() {
  return sessionStorage.getItem("dashboard_api_key");
}

function setStatusClass(element, status) {
  element.classList.remove("status-good", "status-warning", "status-danger", "status-neutral");
  element.classList.add(status);
}

function formatPosture(value) {
  if (!value) {
    return "--";
  }

  return value.replaceAll("_", " ");
}

function formatGuatemalaTime(value) {
  if (!value) {
    return "--";
  }

  const timestamp = value.endsWith("Z") ? value : `${value}Z`;

  return new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Guatemala",
    month: "numeric",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true
  }).format(new Date(timestamp));
}

function updateKeyPanelState() {
  const hasKey = Boolean(getApiKey());

  if (hasKey) {
    elements.apiKeyPanel.classList.add("connected");
    elements.keyPanelStatus.textContent = "Connected";
    elements.keyStatus.textContent = "Dashboard API key saved for this session.";
    elements.apiKeyPanel.open = false;
    return;
  }

  elements.apiKeyPanel.classList.remove("connected");
  elements.keyPanelStatus.textContent = "Not connected";
  elements.keyStatus.textContent = "Enter your dashboard API key to load protected data.";
  elements.apiKeyPanel.open = true;
}

function saveApiKey() {
  const value = elements.apiKey.value.trim();

  if (!value) {
    elements.keyStatus.textContent = "Please enter a valid dashboard API key.";
    return;
  }

  sessionStorage.setItem("dashboard_api_key", value);
  elements.apiKey.value = "";
  elements.apiKeyPanel.classList.add("saved");

  setTimeout(() => {
    elements.apiKeyPanel.classList.remove("saved");
  }, 450);

  updateKeyPanelState();
  loadDashboard();
}

async function apiGet(path, requiresAuth = true) {
  const headers = {
    accept: "application/json"
  };

  if (requiresAuth) {
    const apiKey = getApiKey();

    if (!apiKey) {
      throw new Error("Missing dashboard API key.");
    }

    headers["x-api-key"] = apiKey;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { headers });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

async function loadHealth() {
  const data = await apiGet("/api/device/health", false);

  elements.backendStatus.textContent = data.status;
  elements.backendMessage.textContent = data.message;

  if (data.status === "ready" || data.status === "running") {
    setStatusClass(elements.backendCard, "status-good");
  } else {
    setStatusClass(elements.backendCard, "status-warning");
  }
}

async function loadLatestReading() {
  const data = await apiGet("/api/readings/latest");

  if (!data) {
    elements.currentPosture.textContent = "--";
    elements.currentPostureMeta.textContent = "No readings available.";
    setStatusClass(elements.currentPostureCard, "status-neutral");
    return;
  }

  elements.currentPosture.textContent = formatPosture(data.posture);
  elements.currentPostureMeta.textContent = `Confidence ${(data.confidence * 100).toFixed(0)}% · ${data.device_id}`;

  if (data.posture === "correct" && !data.is_bad_posture) {
    setStatusClass(elements.currentPostureCard, "status-good");
  } else if (data.posture === "not_sitting") {
    setStatusClass(elements.currentPostureCard, "status-warning");
  } else {
    setStatusClass(elements.currentPostureCard, "status-danger");
  }
}

async function loadSummary() {
  const data = await apiGet("/api/reports/summary");

  elements.totalReadings.textContent = data.total_readings ?? "--";
  elements.badPosture.textContent = `${data.bad_posture_percentage ?? 0}%`;
  elements.goodPosture.textContent = `${data.good_posture_percentage ?? 0}%`;
  elements.mostCommon.textContent = data.most_common_posture
    ? formatPosture(data.most_common_posture)
    : "--";
}

async function loadAiAdvice() {
  const data = await apiGet("/api/advice/ai");

  elements.riskLevel.textContent = data.risk_level ?? "--";
  elements.riskMessage.textContent = data.summary
    ? `${data.summary.bad_posture_percentage}% bad posture detected.`
    : "No summary available.";

  if (data.risk_level === "low") {
    setStatusClass(elements.riskCard, "status-good");
  } else if (data.risk_level === "medium") {
    setStatusClass(elements.riskCard, "status-warning");
  } else if (data.risk_level === "high") {
    setStatusClass(elements.riskCard, "status-danger");
  } else {
    setStatusClass(elements.riskCard, "status-neutral");
  }

  elements.aiSource.classList.remove("gemini", "local");

  if (data.source === "gemini") {
    elements.aiSource.textContent = "Generated by Gemini";
    elements.aiSource.classList.add("gemini");
  } else {
    elements.aiSource.textContent = "Local fallback active";
    elements.aiSource.classList.add("local");
  }

  elements.aiAdvice.textContent = data.advice ?? "No advice available.";
}

async function loadHistory() {
  const data = await apiGet(`/api/readings/history?limit=${historyLimit}`);
  const isShowingAll = historyLimit === 1000;

  elements.historyHelper.textContent = isShowingAll
    ? `Showing full history. ${data.length} readings loaded from newest to oldest.`
    : `Showing latest ${data.length} readings from newest to oldest. Use “Load all” to view the full history.`;

  elements.loadAllBtn.textContent = isShowingAll ? "Show latest 10" : "Load all";

  if (!data.length) {
    elements.historyTable.innerHTML = `
      <tr>
        <td colspan="7">No readings available.</td>
      </tr>
    `;
    return;
  }

  elements.historyTable.innerHTML = data.map((item, index) => `
    <tr>
      <td>${data.length - index}</td>
      <td>${item.device_id}</td>
      <td>${item.user_id}</td>
      <td>${formatPosture(item.posture)}</td>
      <td>${item.is_bad_posture ? "Yes" : "No"}</td>
      <td>${(item.confidence * 100).toFixed(0)}%</td>
      <td>${formatGuatemalaTime(item.created_at)}</td>
    </tr>
  `).join("");
}

async function loadDashboard() {
  try {
    await loadHealth();

    if (!getApiKey()) {
      updateKeyPanelState();
      return;
    }

    await Promise.all([
      loadLatestReading(),
      loadSummary(),
      loadAiAdvice(),
      loadHistory()
    ]);

    updateKeyPanelState();
  } catch (error) {
    elements.keyStatus.textContent = error.message;
  }
}

elements.saveKeyBtn.addEventListener("click", saveApiKey);

elements.refreshBtn.addEventListener("click", () => {
  historyLimit = 10;
  loadDashboard();
});

elements.loadAllBtn.addEventListener("click", () => {
  historyLimit = historyLimit === 1000 ? 10 : 1000;
  loadDashboard();
});

updateKeyPanelState();
loadDashboard();
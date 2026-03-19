const socket = io();
const STATE_NAMES = {
    IDLE: "Disattivo", ARMED: "Attivo", ALERT: "Allerta",
    CHALLENGE: "Sfida", DISARMED: "Disinnescato", ALARM: "Allarme"
};
const STATE_COLORS = {
    IDLE: "idle", ARMED: "armed", ALERT: "alert",
    CHALLENGE: "challenge", DISARMED: "disarmed", ALARM: "alarm"
};

function sendCommand(action) {
    fetch("/api/" + action, { method: "POST" });
}

function toggleSettings() {
    document.getElementById("settings-modal").classList.toggle("hidden");
}

function updateStateUI(state) {
    document.getElementById("status-circle").className = STATE_COLORS[state] || "idle";
    document.getElementById("status-text").textContent = STATE_NAMES[state] || state;
    document.getElementById("state-badge").className = "badge " + (STATE_COLORS[state] || "idle");
    document.getElementById("state-badge").textContent = STATE_NAMES[state] || state;
}

socket.on("state_update", function(data) {
    updateStateUI(data.state);
    if (data.state === "CHALLENGE" && data.challenge_remaining) {
        var timerEl = document.getElementById("challenge-timer");
        timerEl.classList.remove("hidden");
        var remaining = data.challenge_remaining;
        timerEl.textContent = remaining + "s";
        if (window._challengeInterval) clearInterval(window._challengeInterval);
        window._challengeInterval = setInterval(function() {
            remaining--;
            timerEl.textContent = Math.max(0, remaining) + "s";
            if (remaining <= 0) clearInterval(window._challengeInterval);
        }, 1000);
    } else {
        document.getElementById("challenge-timer").classList.add("hidden");
        if (window._challengeInterval) clearInterval(window._challengeInterval);
    }
});

socket.on("new_event", function(event) {
    addEventToLog(event);
});

function addEventToLog(event) {
    var list = document.getElementById("event-list");
    var li = document.createElement("li");
    li.className = event.event_type || "";
    var time = event.timestamp ? event.timestamp.split(" ")[1] || "" : "";
    var text = time + " — " + (event.event_type || "");
    if (event.state_from || event.state_to) text += ": " + (event.state_from || "") + " -> " + (event.state_to || "");
    if (event.sensor) text += " (" + event.sensor + ")";
    li.textContent = text;
    list.prepend(li);
}

// Load initial state
fetch("/api/state").then(function(r) { return r.json(); }).then(function(data) {
    updateStateUI(data.state || "IDLE");
});

// Load initial events
fetch("/api/events").then(function(r) { return r.json(); }).then(function(events) {
    events.forEach(function(event) { addEventToLog(event); });
});

// Range slider value display
document.querySelectorAll("input[type=range]").forEach(function(slider) {
    slider.addEventListener("input", function() {
        document.getElementById(slider.id + "-val").textContent = slider.value;
    });
});

// Save settings
function saveSettings() {
    var config = {
        sensors: {
            pir_enabled: document.getElementById("cfg-pir").checked,
            light_enabled: document.getElementById("cfg-light").checked,
            sound_enabled: document.getElementById("cfg-sound").checked
        },
        timing: {
            alert_grace_seconds: parseInt(document.getElementById("cfg-grace").value),
            challenge_timeout_seconds: parseInt(document.getElementById("cfg-timeout").value)
        },
        difficulty: {
            difficulty_level: parseInt(document.getElementById("cfg-difficulty").value)
        }
    };
    fetch("/api/config", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(config)
    });
    toggleSettings();
}

// Load config into settings modal
fetch("/api/config").then(function(r) { return r.json(); }).then(function(cfg) {
    if (cfg.sensors) {
        document.getElementById("cfg-pir").checked = cfg.sensors.pir_enabled;
        document.getElementById("cfg-light").checked = cfg.sensors.light_enabled;
        document.getElementById("cfg-sound").checked = cfg.sensors.sound_enabled;
    }
    if (cfg.timing) {
        document.getElementById("cfg-grace").value = cfg.timing.alert_grace_seconds;
        document.getElementById("cfg-grace-val").textContent = cfg.timing.alert_grace_seconds;
        document.getElementById("cfg-timeout").value = cfg.timing.challenge_timeout_seconds;
        document.getElementById("cfg-timeout-val").textContent = cfg.timing.challenge_timeout_seconds;
    }
    if (cfg.difficulty) {
        document.getElementById("cfg-difficulty").value = cfg.difficulty.difficulty_level;
        document.getElementById("cfg-difficulty-val").textContent = cfg.difficulty.difficulty_level;
    }
});

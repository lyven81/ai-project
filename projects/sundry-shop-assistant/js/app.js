// Sundry Shop Assistant — Adam
// Wires the UI (Welcome, Conversation, 4-mode I/O toggles) to Gemini Live API
// via the FastAPI backend at /ws. Audio streams as PCM; text goes as JSON.

const state = {
  inputMode: localStorage.getItem("ssa_input_mode") || "voice",
  outputMode: localStorage.getItem("ssa_output_mode") || "voice",
  connected: false,
  listening: false,
  currentUserBubble: null,
  currentAgentBubble: null,
};

const media = new MediaHandler();

const client = new GeminiClient({
  onOpen: () => {
    state.connected = true;
    setStatus("Bersambung", true);
  },
  onMessage: (event) => {
    if (typeof event.data === "string") {
      try {
        const msg = JSON.parse(event.data);
        handleServerEvent(msg);
      } catch (err) {
        console.error("Parse error:", err);
      }
    } else {
      // Binary audio bytes from Gemini
      media.playAudio(event.data);
    }
  },
  onClose: () => {
    state.connected = false;
    setStatus("Terputus", false);
  },
  onError: (e) => {
    console.error("WS error:", e);
    setStatus("Ralat sambungan", false);
  },
});

// ---------- Helpers ----------

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function showScreen(id) {
  $$(".screen").forEach((s) => s.classList.remove("active"));
  $(id).classList.add("active");
}

function setStatus(text, active = false) {
  $("#status-text").textContent = text;
  $("#status-dot").classList.toggle("active", active);
}

function addMessage(text, role) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrapper.appendChild(bubble);
  $("#transcript").appendChild(wrapper);
  $("#transcript").scrollTop = $("#transcript").scrollHeight;
  return bubble;
}

function appendToBubble(bubble, text) {
  bubble.textContent += text;
  $("#transcript").scrollTop = $("#transcript").scrollHeight;
}

// ---------- Server events ----------

function handleServerEvent(msg) {
  switch (msg.type) {
    case "user":
      if (state.currentUserBubble) {
        appendToBubble(state.currentUserBubble, msg.text);
      } else {
        state.currentUserBubble = addMessage(msg.text, "user");
      }
      break;

    case "gemini":
      if (state.currentAgentBubble) {
        appendToBubble(state.currentAgentBubble, msg.text);
      } else {
        state.currentAgentBubble = addMessage(msg.text, "agent");
      }
      break;

    case "turn_complete":
      state.currentUserBubble = null;
      state.currentAgentBubble = null;
      break;

    case "interrupted":
      media.stopAudioPlayback();
      state.currentAgentBubble = null;
      break;

    case "tool_call":
      console.log(`[tool] ${msg.name}`, msg.args, "->", msg.result);
      break;

    case "error":
      console.error("Server error:", msg.error);
      addMessage(`Eh, ada masalah kat backend: ${msg.error}. Cuba lagi.`, "agent");
      break;
  }
}

// ---------- Connect / disconnect ----------

async function connectSession() {
  try {
    await media.initializeAudio();
    setStatus("Bersambung...", true);
    client.connect(state.outputMode === "voice" ? "audio" : "text");
  } catch (err) {
    console.error("Connect failed:", err);
    addMessage("Tak boleh connect ke backend. Make sure server dah start.", "agent");
  }
}

function disconnectSession() {
  stopMic();
  client.disconnect();
}

// ---------- Mic ----------

async function startMic() {
  if (!state.connected) await connectSession();
  try {
    // Barge-in: stop any playing audio when user starts speaking
    media.stopAudioPlayback();
    await media.startAudio((pcmBuffer) => {
      if (client.isConnected()) client.send(pcmBuffer);
    });
    state.listening = true;
    $("#mic-btn").classList.add("listening");
    $(".mic-label").textContent = "Mendengar... (tekan untuk berhenti)";
    setStatus("Mendengar", true);
  } catch (err) {
    console.error("Mic start failed:", err);
    addMessage("Tak dapat akses mic. Bagi permission, Pak.", "agent");
  }
}

function stopMic() {
  if (state.listening) {
    media.stopAudio();
    state.listening = false;
    $("#mic-btn").classList.remove("listening");
    $(".mic-label").textContent = "Tekan untuk bertanya";
    setStatus(state.connected ? "Bersambung" : "Sedia", state.connected);
  }
}

function toggleMic() {
  if (state.listening) stopMic();
  else startMic();
}

// ---------- Text input ----------

async function sendText(text) {
  const trimmed = (text || "").trim();
  if (!trimmed) return;
  if (!state.connected) await connectSession();

  // Show user message in transcript immediately (server will also confirm via transcription)
  addMessage(trimmed, "user");

  // Short wait for connect if we just opened the socket
  const waitForConnect = async (ms = 2000) => {
    const start = Date.now();
    while (!client.isConnected() && Date.now() - start < ms) {
      await new Promise((r) => setTimeout(r, 50));
    }
  };
  await waitForConnect();

  client.sendText(trimmed);
}

// ---------- Mode toggles ----------

function setMode(group, mode) {
  if (group === "input") {
    state.inputMode = mode;
    localStorage.setItem("ssa_input_mode", mode);
    $("#voice-input").classList.toggle("active", mode === "voice");
    $("#text-input").classList.toggle("active", mode === "text");
    if (mode === "text") stopMic();
  } else if (group === "output") {
    const changed = state.outputMode !== mode;
    state.outputMode = mode;
    localStorage.setItem("ssa_output_mode", mode);
    // Output mode change requires session reconnect (Live API sets modality at connect)
    if (changed && state.connected) {
      setStatus("Tukar mode...", true);
      stopMic();
      client.disconnect();
      setTimeout(() => connectSession(), 300);
    }
  }

  $$(`.mode-btn[data-group="${group}"]`).forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  });
}

function applyStoredModes() {
  setMode("input", state.inputMode);
  setMode("output", state.outputMode);
}

// ---------- Event wiring ----------

document.addEventListener("DOMContentLoaded", () => {
  // Welcome → Conversation
  $("#start-btn").addEventListener("click", async () => {
    showScreen("#conversation-screen");
    await connectSession();
  });

  // Back button
  $("#back-btn").addEventListener("click", () => {
    disconnectSession();
    showScreen("#welcome-screen");
  });

  // Mic button
  $("#mic-btn").addEventListener("click", toggleMic);

  // Text form
  $("#text-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = $("#text-question");
    await sendText(input.value);
    input.value = "";
  });

  // Mode toggles
  $$(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => setMode(btn.dataset.group, btn.dataset.mode));
  });

  // Preset chips — send as text into the session
  $$(".chip-clickable").forEach((chip) => {
    chip.addEventListener("click", async () => {
      await sendText(chip.dataset.preset || chip.textContent);
    });
  });

  applyStoredModes();
});

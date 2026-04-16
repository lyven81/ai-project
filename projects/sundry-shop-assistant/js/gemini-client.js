// GeminiClient: WebSocket wrapper to the backend /ws endpoint.

class GeminiClient {
  constructor(config) {
    this.websocket = null;
    this.onOpen = config.onOpen;
    this.onMessage = config.onMessage;
    this.onClose = config.onClose;
    this.onError = config.onError;
  }

  connect(outputMode = "audio") {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws?mode=${outputMode}`;

    this.websocket = new WebSocket(wsUrl);
    this.websocket.binaryType = "arraybuffer";

    this.websocket.onopen = () => { if (this.onOpen) this.onOpen(); };
    this.websocket.onmessage = (e) => { if (this.onMessage) this.onMessage(e); };
    this.websocket.onclose = (e) => { if (this.onClose) this.onClose(e); };
    this.websocket.onerror = (e) => { if (this.onError) this.onError(e); };
  }

  send(data) {
    if (this.isConnected()) this.websocket.send(data);
  }

  sendText(text) {
    this.send(JSON.stringify({ text }));
  }

  disconnect() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }

  isConnected() {
    return this.websocket && this.websocket.readyState === WebSocket.OPEN;
  }
}

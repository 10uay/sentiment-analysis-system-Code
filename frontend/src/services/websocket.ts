export function createAnalysisSocket(onMessage: (data: unknown) => void) {
  const url = import.meta.env.VITE_WS_URL || "ws://localhost:8000/api/v1/ws/analyze";
  const socket = new WebSocket(url);

  socket.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch {
      onMessage(event.data);
    }
  };

  return socket;
}

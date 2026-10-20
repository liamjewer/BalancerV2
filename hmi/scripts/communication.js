const PORT = 3683;

const ws = new WebSocket(`ws://${location.hostname}:${PORT}`);

clientConsole = document.getElementById("console")

ws.onopen = () => console.log("connected to " + PORT);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);

  switch (msg.type) {
    case "console":
      clientConsole.insertAdjacentText("beforeend", "B-V2: " + msg.value + "\n");
      break;
    default:
      console.log("received:", msg);
      break;
  }
};

ws.onclose = () => console.log("disconnected");
ws.onerror = (err) => console.log("error", err);

function send(type, value) {
  if (ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ type: type, value: value }));
}
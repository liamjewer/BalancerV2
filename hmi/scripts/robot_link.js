const PORT = 3683;

const ws = new WebSocket(`ws://${location.hostname}:${PORT}`);

clientConsole = document.getElementById("console");
connectionIndicator = document.getElementById("connection");


ws.onopen = () => {
  console.log("connected to " + PORT);

  send("disable", "true")
  displayConnected();
};

ws.onmessage = (event) => {const PORT = 3683;

const ws = new WebSocket(`ws://${location.hostname}:${PORT}`);

clientConsole = document.getElementById("console");
connectionIndicator = document.getElementById("connection");


ws.onopen = () => {
  console.log("connected to " + PORT);

  displayConnected();
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);

  switch (msg.type) {
    case "console":
      clientConsole.insertAdjacentText("beforeend", "B-V2: " + msg.value + "\n");
      // keeps the most current message on the bottom
      clientConsole.scrollTop = clientConsole.scrollHeight;
      break;
    default:
      console.log("received:", msg);
      break;
  }
};

ws.onclose = () => {
  console.log("disconnected");

  displayDisconnected();
};

ws.onerror = (err) => {
  console.log("error", err);

  displayDisconnected();
};
  const msg = JSON.parse(event.data);

  switch (msg.type) {
    case "console":
      clientConsole.insertAdjacentText("beforeend", "B-V2: " + msg.value + "\n");
      // keeps the most current message on the bottom
      clientConsole.scrollTop = clientConsole.scrollHeight;
      break;
    case "state":
      document.getElementById("stateReadout").textContent = msg.value
    default:
      console.log("received:", msg);
      break;
  }
};

ws.onclose = () => {
  console.log("disconnected");

  displayDisconnected();
};

ws.onerror = (err) => {
  console.log("error", err);

  displayDisconnected();
};

function send(type, value) {
  console.log("sending...");
  if (ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ type: type, value: value }));
}

function displayConnected(){
  connectionIndicator.classList.add("connected");
  connectionIndicator.getElementsByTagName("svg")[0].setAttribute('data-lucide', 'globe');

  lucide.createIcons(); //re-render
}

function displayDisconnected(){
  connectionIndicator.classList.remove("connected");
  connectionIndicator.getElementsByTagName("svg")[0].setAttribute('data-lucide', 'globe-off');

  lucide.createIcons(); //re-render
}
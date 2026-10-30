const PORT = 3683;

const ws = new WebSocket(`ws://${location.hostname}:${PORT}`);

clientConsole = document.getElementById("console");
connectionIndicator = document.getElementById("connection");

robotPingTime = 0.0;
robotPongTime = 0.0;
robotLatency = 0.0;


ws.onopen = () => {
  console.log("connected to " + PORT);

  send("disable", "true")
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
    case "pyPong":
      robotPongTime = performance.now();
      robotLatency = robotPongTime - robotPingTime;
      hmiLat = document.getElementById("hmiLat");
      hmiLat.style = "--p: " + (1.0-(robotLatency/100)) + ";";
      hmiLat.querySelector('.reading').textContent = robotLatency.toFixed(2) + " ms";
      break;
    case "loop_hz":
      controlFrequency = document.getElementById("controlFreq");
      controlFrequency.style = "--p: " + (msg.value/200) + ";";
      controlFrequency.querySelector('.reading').textContent = msg.value.toFixed(2) + " Hz";
      break;
    case "cpp_lat":
      pipeLat = document.getElementById("pipeLat");
      pipeLat.style = "--p: " + (1.0-(msg.value/1000)) + ";";
      pipeLat.querySelector('.reading').textContent = msg.value.toFixed(2) + " μs";
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
  

function send(type, value) {
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
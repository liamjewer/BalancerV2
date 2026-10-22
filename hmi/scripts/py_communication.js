const PY_PORT = 3683;

const pyWS = new WebSocket(`ws://${location.hostname}:${PY_PORT}`);

clientConsole = document.getElementById("console");
connectionIndicator = document.getElementById("connection");


pyWS.onopen = () => {
  console.log("connected to " + PY_PORT);

  displayConnected();
};

pyWS.onmessage = (event) => {
  
  const PY_PORT = 3683;
  const pyWS = new WebSocket(`ws://${location.hostname}:${PY_PORT}`);

  clientConsole = document.getElementById("console");
  connectionIndicator = document.getElementById("connection");


  pyWS.onopen = () => {
    console.log("connected to " + PY_PORT);

    displayConnected();
  };

  pyWS.onmessage = (event) => {
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

  pyWS.onclose = () => {
    console.log("disconnected");

    displayDisconnected();
  };

  pyWS.onerror = (err) => {
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
    default:
      console.log("received:", msg);
      break;
  }
};

pyWS.onclose = () => {
  console.log("disconnected");

  displayDisconnected();
};

pyWS.onerror = (err) => {
  console.log("error", err);

  displayDisconnected();
};

function sendPy(type, value) {
  if (pyWS.readyState !== WebSocket.OPEN) return;
  pyWS.send(JSON.stringify({ type: type, value: value }));
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
const CPP_PORT = 4917;

const cppWS = new WebSocket(`ws://${location.hostname}:${CPP_PORT}`);

clientConsole = document.getElementById("console");
connectionIndicator = document.getElementById("connection");


cppWS.onopen = () => {
  console.log("connected to " + CPP_PORT);

  displayConnected();
};

cppWS.onmessage = (event) => {
  
  const CPP_PORT = 3683;
  const cppWS = new WebSocket(`ws://${location.hostname}:${CPP_PORT}`);

  clientConsole = document.getElementById("console");
  connectionIndicator = document.getElementById("connection");


  cppWS.onopen = () => {
    console.log("connected to " + CPP_PORT);

    displayConnected();
  };

  cppWS.onmessage = (event) => {
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

  cppWS.onclose = () => {
    console.log("disconnected");

    displayDisconnected();
  };

  cppWS.onerror = (err) => {
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

cppWS.onclose = () => {
  console.log("disconnected");

  displayDisconnected();
};

cppWS.onerror = (err) => {
  console.log("error", err);

  displayDisconnected();
};

function sendCpp(type, value) {
  if (cppWS.readyState !== WebSocket.OPEN) return;
  cppWS.send(JSON.stringify({ type: type, value: value }));
}
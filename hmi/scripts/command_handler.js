const EStopButton = document.getElementById("EstopButton"); // safety #1>
const enabledToggle = document.getElementById("enabled");
const commandPad = document.getElementsByClassName("key");

// shutdown button listener
EStopButton.addEventListener("click", () => { // safety #1 priority
    send("ESTOP", true);
});

// enable toggle handling
enabledToggle.addEventListener('change', (event) => {
  if (event.target.checked) {
    send("enable", true) //send enable signal
  } else {
    send("disable", true)
  }
});

[...commandPad].forEach(key => {
  key.addEventListener("click", () => {
    // only send state update if robot is not disabled
    if(document.getElementById("stateReadout").textContent != "DISABLED") send("command", key.dataset.action);
  });
});
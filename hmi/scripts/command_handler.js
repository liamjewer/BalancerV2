// HTML elements
const EStopButton = document.getElementById("EstopButton"); // safety #1>
const enabledToggle = document.getElementById("enabled");
const commandPad = document.getElementsByClassName("key");

// controller IDs
const AXES = ["leftJoystickX", "leftJoystickY", "rightJoystickX", "rightJoystickY"];
const BUTTONS = {
  0: "aButton", 1: "bButton", 2: "xButton", 3: "yButton",
  4: "leftBumper", 5: "rightBumper",
  8: "viewButton", 9: "startButton",
  12: "padUp", 13: "padDown", 14: "padLeft", 15: "padRight",
  16: "xboxButton"
};
const TRIGGERS = { 6: "leftTrigger", 7: "rightTrigger" };
const PUSH_FREQ = 60;//Hz 

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

function readGamepadJSON() {
  const pad = navigator.getGamepads().find(p => p !== null);
  if (!pad) return null;

  const out = {};
  AXES.forEach((name, i) => { out[name] = pad.axes[i]; });
  for (const [i, name] of Object.entries(BUTTONS)) out[name] = pad.buttons[i].pressed;
  for (const [i, name] of Object.entries(TRIGGERS)) out[name] = pad.buttons[i].value;

  return JSON.stringify(out);
}

const timerId = setInterval(() => {
  send("gamepad", readGamepadJSON());
}, (1/PUSH_FREQ)*1000); // convert HZ to ms
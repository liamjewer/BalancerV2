const shutdownButton = document.querySelector('[data-action="shutdown"]'); // safety #1>
const enabledToggle = document.getElementById("enabled");

shutdownButton.addEventListener("click", () => { // safety #1 priority
    send("ESTOP", true);
});

enabledToggle.addEventListener('change', (event) => {
  if (event.target.checked) {
    send("enable", true) //send enable signal
  } else {
    send("disable", true)
  }
});
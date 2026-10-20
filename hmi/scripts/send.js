const sendButton = document.getElementById('send');

sendButton.addEventListener('click', () => {
    consoleMsg = document.getElementById("consoleMsg");
    send("console", consoleMsg.value);
    clientConsole.insertAdjacentText("beforeend", "Me: " + consoleMsg.value + "\n");

    //reset messagebox
    consoleMsg.value = "";

    sendButton.classList.add('sent');
});

sendButton.addEventListener('animationend', () => {
    sendButton.classList.remove('sent');   // ready to trigger again
});
const sendButton = document.getElementById('send');

sendButton.addEventListener('click', () => {
    sendButton.classList.add('sent');
});

sendButton.addEventListener('animationend', () => {
    sendButton.classList.remove('sent');   // ready to trigger again
});
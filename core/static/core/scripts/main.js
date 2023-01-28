/* Toggles the upload loader div */
function toggle_loader() {
    const e = document.querySelector('.loader_div');
    if(e.style.display == 'none')
        e.style.display = 'block';
    else
        e.style.display = 'none';
}

/* Closes the popup messages */
function closeMsg() {
    const msg = document.querySelector('.message-header')
    msg.parentNode.removeChild(msg);
}
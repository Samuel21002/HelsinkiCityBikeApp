/* Toggles the upload loader div */
function toggle_loader() {
    const e = document.querySelector('.loader_div');
    if(e.style.display == 'none')
        e.style.display = 'block';
    else
        e.style.display = 'none';
};

/* Closes the popup messages */
function closeMsg() {
    const msg = document.querySelector('.message-header')
    msg.parentNode.removeChild(msg);
};

document.addEventListener("DOMContentLoaded", function () {
    const nav = document.querySelector('.navbar-burger');
    nav.addEventListener('click', () => {
        let burger_div = document.getElementById('burger-div');
        if (burger_div.style.display == 'none') {
            burger_div.style.display = 'block';
        } else {
            burger_div.style.display = 'none';
        }
    });
});
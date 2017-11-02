$(document).ready(function () {
    var socket = new WebSocket('ws://' + window.location.host + '/gameRoom/');
    
    socket.onopen = function open() {
        console.log('WebSockets connection created.');
    };

    if (socket.readyState == WebSocket.OPEN) {
        socket.onopen();
    }
});
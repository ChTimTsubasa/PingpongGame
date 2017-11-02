$(document).ready(function () {
    var socket = new WebSocket('ws://' + window.location.host + '/chat');
    
    socket.onmessage = function(e) {
        alert(e.data);
    }

    socket.onopen = function() {
        socket.send("hello world");
    }
});
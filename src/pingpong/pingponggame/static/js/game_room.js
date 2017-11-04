function playerUpdate() {
    var creator_id = data.players[0].creator_id;
    var ori_creator = $("#creator").children('div');
    if (creator_id != "") {
        ori_creator.replaceWith(data.players[0].html);
    }
}

$(document).ready(function () {
    var socket = new WebSocket('ws://' + window.location.host + '/chat');
    
    socket.onmessage = function(e) {
        alert(e.data);
    }

    socket.onopen = function() {
        socket.send("hello world");
    }

    socket.onclose = function() {
        socket.send("closing");
    }
});
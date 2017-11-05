function playerUpdate() {
    var creator_id = data.players[0].creator_id;
    var ori_creator = $("#creator").children('div');
    if (creator_id != "") {
        ori_creator.replaceWith(data.players[0].html);
    }
}

function handle(message) {
    console.log(message)
    if (message.TYPE == 'STATE') {
        if (message.state == 'ready') {
            $('#win_but').prop('disabled', false);
        } else {
            $('#win_but').prop('disabled', true);
        }
    }
}

$(document).ready(function () {
    var socket = new WebSocket('ws://' + window.location.host + '/game$');
    
    socket.onmessage = function(e) {
        var data = jQuery.parseJSON(e.data)
        handle(data);
    }

    socket.onopen = function() {
        // socket.send("hello world");
    }

    socket.onclose = function() {
        socket.close();
    }

    $('#win_but').prop('disabled', true);
    // $('#win_but').click(function() {
    //     websocket.send(JSON.stringify({
    //         TYPE: "GAME",
    //         player: $('player').val(),
    //     }));
    // })
});
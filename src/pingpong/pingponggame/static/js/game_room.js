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

//send requets to get player information inside room up-to-date
function sendRequest() {
    gameid = $('#game').val();
    $.getJSON("getPlayersInfo/"+gameid, function(data) {
        updatePlayerInfo(data);
    });
}

//Update player information in web page
function updatePlayerInfo(data) {
    players = data.players;
    console.log(players);
    // $('#creator').val(players[0].html);
    // $('#opponent').val(players[1].html);
    // $('#creator').replaceWith(players[0].html);
    // $('#opponent').replaceWith(players[1].html);
    $('#creator').html(players[0].html);
    $('#opponent').html(players[1].html);
}


$(document).ready(function () {
    var socket = new WebSocket('ws://' + window.location.host + '/game$');
    
    window.setInterval(sendRequest, 1000);
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
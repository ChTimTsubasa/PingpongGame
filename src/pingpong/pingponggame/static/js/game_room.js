function handle(message) {
    // console.log(message)
    console.log(message.TYPE)
    switch (message.TYPE) {
        case 'STATE':
            if (message.STATE == 'start') {
                $('#win_but').prop('disabled', false);
            } else {
                $('#win_but').prop('disabled', true);
            }
            break;
        case 'PAD':
            console.log(message)
            break;
        case 'BALL':
            console.log(message)
            break;
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
    // console.log(players);

    $('#creator').html(players[0].html);
    $('#opponent').html(players[1].html);
}

$(document).ready(function () {
    var game_id = $('#game').val()
    var socket = new WebSocket('ws://' + window.location.host + '/game/' + game_id);

    sendRequest();
    window.setInterval(sendRequest, 1000);
    var d = new Date();

    socket.onmessage = function(e) {
        var data = jQuery.parseJSON(e.data)
        handle(data);
    }

    socket.onopen = function() {
    }

    socket.onclose = function() {
        socket.close();
    }

    $('#win_but').prop('disabled', true);

    $('#win_but').click(function() {
        console.log ("button clicked")
        socket.send(JSON.stringify({
            TYPE: "STATE",
            state: 'ready',
        }));

        $('#win_but').prop('disabled', true);
    })
});

//Update scoreboard information in web page
function updateGameInfo(data) {
    $('#latest_game').val(data.latest_game);
    if (data.games.length != null) {
        for (var i = 0; i < data.games.length; i++) {
            var gameRecord = data.games[i];
            console.log(gameRecord.html);
            $('#scoreboard').find('tbody').prepend(gameRecord.html);
        }
    }
}


function sendScoreBoardRequest() {
    gameid = $('#latest_game').val();
    $.getJSON("getLatestGame/"+gameid, function(data) {
        updateGameInfo(data);
    });
}

$(document).ready(function () {
    sendScoreBoardRequest();
    window.setInterval(sendScoreBoardRequest, 5000);
});
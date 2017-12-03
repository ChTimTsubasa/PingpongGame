//Update scoreboard information in web page
function updateGameInfo(data) {
    $('#latest_game').val(data.latest_game);
    if (data.games.length != 0) {
        for (var i = 0; i < data.games.length; i++) {
            var gameRecord = data.games[i];
            console.log(gameRecord);
            $('#scoreboard').find('tbody').prepend(gameRecord);
        }
    }
}


function sendScoreBoardRequest() {
    gameid = $('#latest_game').val();
    $.getJSON("getLatestGame/"+gameid, function(data) {

        console.log(data)
        updateGameInfo(data);
    });
}

$(document).ready(function () {
    sendScoreBoardRequest();
    window.setInterval(sendScoreBoardRequest, 5000);
});
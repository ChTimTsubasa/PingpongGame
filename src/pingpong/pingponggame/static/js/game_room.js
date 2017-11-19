// // function playerUpdate() {
// //     var creator_id = data.players[0].creator_id;
// //     var ori_creator = $("#creator").children('div');
// //     if (creator_id != "") {
// //         ori_creator.replaceWith(data.players[0].html);
// //     }
// // }

// console.log('generating game_room.js!!!!!!!!!!');

// function handle(message) {
//     console.log(message)
//     if (message.TYPE == 'STATE') {
//         if (message.state == 'ready') {
//             $('#win_but').prop('disabled', false);
//         } else {
//             $('#win_but').prop('disabled', true);
//         }
//     } else if (message.TYPE == "GAME") {
//         alert('winner is ' + message.winner);
//     }
// }

// //send requets to get player information inside room up-to-date
// function sendRequest() {
//     gameid = $('#game').val();
//     $.getJSON("getPlayersInfo/"+gameid, function(data) {
//         updatePlayerInfo(data);
//     });
// }

// //Update player information in web page
// function updatePlayerInfo(data) {
//     players = data.players;
//     console.log(players);

//     $('#creator').html(players[0].html);
//     $('#opponent').html(players[1].html);
// }


// $(document).ready(function () {
//     console.log('game room ready')

//     setTimeout(function() {
//         console.log('timeout done');
//         var socket = new WebSocket('ws://' + window.location.host);
//         sendRequest();
//         window.setInterval(sendRequest, 1000);

//         window.setInterval(sendPosition, 300);
//         // window.setInterval(findBrick, 300);


//         socket.onmessage = function(e) {
//             var data = jQuery.parseJSON(e.data)
//             handle(data);
//         }

//         socket.onopen = function() {
//             // socket.send("hello world");
//         }

//         socket.onclose = function() {
//             socket.close();
//         }

//         $('#win_but').prop('disabled', true);

//         $('#win_but').click(function() {
//             console.log ("button clicked")
//             socket.send(JSON.stringify({
//                 TYPE: "GAME",
//                 score: Math.floor(1 + Math.random() * 10)
//             }));

//             $('#win_but').prop('disabled', true);
//         })
//     }
//     , 10000);
    
// });
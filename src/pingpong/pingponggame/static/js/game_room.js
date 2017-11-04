// CSRF set-up copied from Django docs
// From todo.js
function getCookie(name) {  
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function playerUpdate() {
    var game = $('#game').val();
    url = "getPlayersInfo/" + game;
    $.getJSON(url)
        .done( function(data) {
            console.log(data)
        });
}

$(document).ready(function () {
    var socket = new WebSocket('ws://' + window.location.host + '/chat');
    
    socket.onmessage = function(e) {
        alert(e.data);
    }

    socket.onopen = function() {
        socket.send("hello world");
    }

    console.log("here")

    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });
    playerUpdate();
    console.log("here")
    window.setInterval(playerUpdate, 5000);
});
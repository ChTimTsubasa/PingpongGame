(function() {

  console.log('example.js file !!!22222222222222222222');

  var body = document.body;
  var loading = document.createElement('class');
  loading.className = 'loading';
  if (Stage._supported) {
    loading.innerHTML = 'Loading...';
    loading.style.zIndex = -1;
  } else {
    loading.innerHTML = 'Please use a <a target="_blank" href="https://www.google.com/search?q=modern+browser">modern browser!';
    loading.style.zIndex = 0;
  }
  body.insertBefore(loading, body.firstChild);

// function playerUpdate() {
//     var creator_id = data.players[0].creator_id;
//     var ori_creator = $("#creator").children('div');
//     if (creator_id != "") {
//         ori_creator.replaceWith(data.players[0].html);
//     }
// }

})();

var status = (function() {

  console.log('22222222222222222222');
  var el = null;
  return function(msg) {
    if (el === null) {
      var el = document.createElement('div');
      el.style.position = 'absolute';
      el.style.color = 'black';
      el.style.background = 'white';
      el.style.zIndex = 999;
      el.style.top = '5px';
      el.style.right = '5px';
      el.style.padding = '1px 5px';
      document.body.appendChild(el);
    }
    el.innerHTML = msg;
  };
})();

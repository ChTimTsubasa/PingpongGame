ClientStatus = {
  WAIT :      1,  // Wait for another user
  PREPARING : 2,  // Being in unready status
  GAMING :    3,  // Game is started
  PAUSE :     4,  // Game is paused for [1 user lose point] [some one jump out]
  END :       5,  // Game is ended
}

EventInput = {
  ALL_IN :    1,  // All users are in
  ONE_OUT :   2,  // One of the user ready
  START :     3,  // Server send an Start command 
  SCORE :     4,  // Server send a score indicating one is win
  ONE_WIN :   5,  // One of the user wins
}

var P2DEBUG = false;
var paddle;
var paddle2;
var ball;
var socket;
var padIntervalID;
var client_status = 0;

//pop up an alert box
function popAlert() {
  confirm("Someone scored");
  socket.send(JSON.stringify({
    TYPE: "STATE",
    STATE: 'ready',
    VAL: true,
  }));
}

function popAlert_redirect() {
  confirm("Game is Over");
  // redirect to main page
  window.location.href = 'http://' + window.location.host + '/main';
}


function sendBall() {
  socket.send(JSON.stringify({
    TYPE: "BALL",
    p_x: ball.position[0],
    p_y: ball.position[1],
    v_x: ball.velocity[0],
    v_y: ball.velocity[1],
  }));
}

function sendPad() {
  socket.send(JSON.stringify({
    TYPE: "PAD",
    x: paddle.position[0],
    y: paddle.position[1],
  }));
}

function sendLoseScore() {
  socket.send(JSON.stringify({
    TYPE: "STATE",
    STATE: "lose_score",
  }));
}


function Physics(ui, width, height) {

  var world = this.world = new p2.World({
    gravity : [ 0, 0 ],
    defaultFriction : 0
  });

  world.solver.stiffness = Number.MAX_VALUE;

  var ballMater = new p2.Material();
  var wallMater = brickMater = paddleMater = new p2.Material();

  world.addContactMaterial(new p2.ContactMaterial(ballMater, wallMater, {
    restitution : 1.0,
  }));

  var vwallShape = new p2.Line(25, 1);
  vwallShape.material = wallMater;

  var hwallShape = new p2.Line(18, 1);
  hwallShape.material = wallMater;

  var ballShape = new p2.Circle(0.5);
  ballShape.material = ballMater;

  var fullPaddleShape = new p2.Convex([ [ 1.8, -0.1 ], [ 1.8, 0.1 ],
      [ 1.2, 0.4 ], [ 0.4, 0.6 ], [ -0.4, 0.6 ], [ -1.2, 0.4 ], [ -1.8, 0.1 ],
      [ -1.8, -0.1 ] ]);
  fullPaddleShape.material = paddleMater;

  var BALL = 1, WALL = 2;
  
  vwallShape.collisionGroup = WALL;
  hwallShape.collisionGroup = WALL;
  fullPaddleShape.collisionGroup = WALL;
  ballShape.collisionGroup = BALL;

  vwallShape.collisionMask = BALL;
  hwallShape.collisionMask = BALL;
  fullPaddleShape.collisionMask = BALL;
  ballShape.collisionMask = WALL;

  var leftWall = new p2.Body({
    position : [ +9, -0.5 ],
    angle : Math.PI / 2,
    mass : 0,
  });
  leftWall.addShape(vwallShape);
  leftWall.ui = null;
  world.addBody(leftWall);

  var rightWall = new p2.Body({
    position : [ -9, -0.5 ],
    angle : Math.PI / 2,
    mass : 0
  });
  rightWall.addShape(vwallShape);
  rightWall.ui = null;
  world.addBody(rightWall);

  // var topWall = new p2.Body({
  //   position : [ 0, +12.5 ],
  //   mass : 0
  // });
  // topWall.addShape(hwallShape);
  // topWall.ui = null;
  // world.addBody(topWall);

  var bottomWall = new p2.Body({
    position : [ 0, -12.5 ],
    mass : 0
  });
  bottomWall.addShape(hwallShape);
  bottomWall.isBottom = true;
  bottomWall.ui = null;
  world.addBody(bottomWall);

  var fullPaddle = new p2.Body({
    position : [ 0, -7 ],
    mass : 0
  });

  fullPaddle.paddleWidth = 3;
  fullPaddle.addShape(fullPaddleShape);
  fullPaddle.isPaddle = true;
  fullPaddle.motionState = p2.Body.STATIC;
  ui.fullPaddle(fullPaddle);


  var fullPaddle2 = new p2.Body({
    position : [ 0, 7 ],
    mass : 0
  });
  fullPaddle2.paddleWidth = 3;
  fullPaddle2.addShape(fullPaddleShape);
  fullPaddle2.isPaddle = false;
  fullPaddle2.motionState = p2.Body.STATIC;
  ui.fullPaddle2(fullPaddle2);
  

  paddle = fullPaddle;
  world.addBody(paddle);


  paddle2 = fullPaddle2;
  world.addBody(paddle2);


  function setPaddle(neo) {
    if (paddle !== neo) {
      world.removeBody(paddle);
      neo.position[0] = paddle.position[0];
      neo.velocity[0] = paddle.velocity[0];
      world.addBody(paddle = neo);
    }
  }

  function setPaddle2(neo) {
    if (paddle2 !== neo) {
      world.removeBody(paddle2);
      neo.position[0] = paddle2.position[0];
      neo.velocity[0] = paddle2.velocity[0];
      world.addBody(paddle2 = neo);
    }
  }

  function makeBall(pos) {
    var body = new p2.Body({
      mass : 1
    });
    if (pos) {
      body.position = pos;
    }
    body.damping = 0;
    body.angularDamping = 0;
    body.addShape(ballShape);
    body.isBall = true;
    ui.newBall(body);
    world.addBody(body);
    return body;
  }


  world.on('impact', function(evt) {
    var a = evt.bodyA, b = evt.bodyB;
    var ball = a.isBall && a || b.isBall && b;
    var bottom = a.isBottom && a || b.isBottom && b;
    var paddle = a.isPaddle && a || b.isPaddle && b;

    if (ball) {
      var speed = ui.ballSpeed();
      var velocity = ball.velocity;

      if (velocity[1] >= 0) {
        velocity[1] = Math.max(velocity[1], speed / 3);
      } else {
        velocity[1] = Math.min(velocity[1], -speed / 3);
      }
      var fix = speed
          / Math.sqrt(velocity[0] * velocity[0] + velocity[1] * velocity[1]);
      velocity[0] *= fix, velocity[1] *= fix;

      ball.angularVelocity = ball.angle = 0;

      if (bottom) {
        console.log('lose one score')
        world.removeBody(ball);
        sendLoseScore();

      } else if (paddle) {
        ui.hitPaddle(paddle);
        console.log('hit pad');
        sendBall();
      }
    }
  });

  function findBall() {
    for (var i = 0; i < world.bodies.length; i++) {
      if (world.bodies[i].isBall) {
        return world.bodies[i];
      }
    }
  }
  this.findBall = findBall;

  this.initGame = function() {
    for (var i = world.bodies.length - 1; i >= 0; i--) {
      var body = world.bodies[i];
      if (body.isBrick || body.isBall || body.isDrop) {
        world.removeBody(body);
      }
    }

    setPaddle(fullPaddle);
    setPaddle2(fullPaddle2);
    makeBall([ 0, -5 ]);
  };

  this.startGame = function() {
    ball = findBall();
    var a = Math.PI * 0.3 * 0.4 - 0.2;
    var speed = ui.ballSpeed();
    ball.velocity = [ speed * Math.sin(a) * 0.6, speed * Math.cos(a) * 0.6 ];
  };

  this.gameOver = function() {
    for (var i = world.bodies.length - 1; i >= 0; i--) {
      var body = world.bodies[i];
      if (body.isBall) {
        world.removeBody(body);
      }
    }
    // TODO: send a game end message
  };


  this.addBall = function() {
    var oldball = findBall();
    var newball = makeBall();
    newball.position[0] = oldball.position[0];
    newball.position[1] = oldball.position[1];
    newball.velocity[0] = -oldball.velocity[0];
    newball.velocity[1] = -oldball.velocity[1];
  };

  var paddleTo = 0;

  this.movePaddle = function(x) {
    paddleTo = x;
  };

  var paddleTo2 = 0;
  this.movePaddle2 = function(x) {
    paddleTo2 = x;
  };


  this.fullPaddle = function() {
    setPaddle(fullPaddle);
  };

  this.fullPaddle2 = function() {
    setPaddle2(fullPaddle2);
  };


  this.tick = function(t) {
    var balls = 0;
    for (var i = world.bodies.length - 1; i >= 0; i--) {
      var body = world.bodies[i];
      // remove ball if passed through walls
      if (Math.abs(body.position[0]) > width / 2
          || Math.abs(body.position[1]) > height / 2) {
        world.removeBody(body);
      } else if (body.isBall) {
        balls++;
      }
    }
    if (balls < 1) {
      ui.gameOver();
    }

    if (paddleTo !== paddle.position[0]) {
      var padx = paddle.position[0];
      var wallLimit = 9 - paddle.paddleWidth / 2;
      var speedLimit = ui.paddleSpeed() * t / 1000;
      if (paddleTo > padx) {
        paddle.position[0] = Math.min(paddleTo, padx + speedLimit, wallLimit);
      } else if (paddleTo < padx) {
        paddle.position[0] = Math.max(paddleTo, padx - speedLimit, -wallLimit);
      }
    }
    if (paddleTo2 !== paddle2.position[0]) {
      var padx = paddle2.position[0];
      var wallLimit = 9 - paddle2.paddleWidth / 2;
      var speedLimit = ui.paddleSpeed() * t / 1000;
      if (paddleTo2 > padx) {
        paddle2.position[0] = Math.min(paddleTo2, padx + speedLimit, wallLimit);
      } else if (paddleTo2 < padx) {
        paddle2.position[0] = Math.max(paddleTo2, padx - speedLimit, -wallLimit);
      }
    }

  };

}

Stage(function(stage) {
  // var STORE_KEY = 'breakout-v1';
  var width = 20, height = 26;
  var state = {
    // max : 0,
    ready : false,
    playing : false
  };

  stage.MAX_ELAPSE = 100;

  stage.viewbox(width * 16, height * 1.12 * 16).pin('offsetY',
      -height * 0.04 * 16).pin('align', -0.5);

  var pscale = 16;

  var physics = new Physics({
    newBall : function(body) {
      body.ui = Stage.image('ball', 10).pin({
        'handle' : 0.5,
        'scale' : 1 / pscale
      });
    },
    // hitPaddle : function() {
    //   // state.combo = 1;
    // },
    hitBottom : function() {
      !physics.findBall() && gameOver();
    },
    fullPaddle : function(body) {
      body.ui = Stage.image('paddleFull').pin({
        'handle' : 0.5,
        'scale' : 1 / pscale
      });
    },
    fullPaddle2 : function(body) {
      body.ui = Stage.image('paddleFull').pin({
        'handle' : 0.5,
        'scale' : 1 / pscale
      });
    },
    gameOver : function() {
      gameOver();
    },
    paddleSpeed : function() {
      return 20;
    },
    ballSpeed : function() {
      return (10);
    }
  }, width, height);

  var board = Stage.image('board').appendTo(stage).pin('handle', 0.5).attr(
      'spy', true);

  var p2view = new Stage.P2(physics.world, {
    lineWidth : 1 / pscale,
    lineColor : '#888',
    ratio : 4 * pscale,
    debug : P2DEBUG
  }).attr('spy', true).pin({
    'align' : 0.5,
    'scale' : pscale
  }).appendTo(board);
  //User use mouse to move paddle
  // p2view.on([ Mouse.START, Mouse.MOVE ], function(point) {
  //   physics.movePaddle(point.x);
  // });
  //When user press keyboard arrowleft and arroweight
  document.onkeydown = function(e) {
    stage.touch();
    e = e || window.event;
    keyboard.down(e.code);
    console.log(e.code);
  };
  var keyboard = {
    down : function(code) {
      if (code == 'ArrowLeft') {
        physics.movePaddle(paddle.position[0] - 3);
      }

      if (code == 'ArrowRight') {
        physics.movePaddle(paddle.position[0] + 3);
      }
    }
  };  

  var restart = Stage.image('restart').appendTo(board).pin({
    align : 0.5,
  });
  
  stage.tick(function(t) {
    if (state.playing) {
      physics.tick(t);
    }
  });

  // try {
  //   state.max = localStorage.getItem(STORE_KEY) || 0;
  // } catch (e) {
  // }

  initGame();

  function initGame() {
    if (!state.ready) {
      p2view.tween(100).pin('alpha', 1);
      restart.hide();
      physics.initGame();
    }
    state.ready = true;
  }

  function startGame() {
    initGame();
    state.ready = false;
    physics.startGame();
    Timeout.loop(function() {
      return nextTime();
    }, nextTime());
    state.playing = true;
  }

  function gameOver() {
    state.playing = false;
    // try {
    //   localStorage.setItem(STORE_KEY, state.max);
    // } catch (e) {
    // }
    physics.gameOver();
    // restart.show();
    // p2view.tween(100).pin('alpha', 0.5);
    Timeout.reset();
  }

  function nextTime() {
    return 8000; 
  }

function fireGame(dir) {
  startGame();
  if (dir == -1) {
    ball.position[1] = -ball.position[1];
    ball.velocity[0] = -ball.velocity[0];
    ball.velocity[1] = -ball.velocity[1];
  }

  padIntervalID = window.setInterval(sendPad, 100);
}

function pauseGame() {
  window.clearInterval(padIntervalID);
  gameOver();
}

function handle(message) {
  console.log(message)
  switch (message.TYPE) {
    case 'EVENT':
      status_trans(message);
      break;
    case 'PAD':
      physics.movePaddle2(-message.x);
      break;
    case 'BALL':
      ball.position[0] = -message.p_x;
      ball.position[1] = -message.p_y;
      ball.velocity[0] = -message.v_x;
      ball.velocity[1] = -message.v_y;
      break;
  }
}

//send requets to get player information inside room up-to-date
function sendRequest() {
  gameid = $('#game').val();
  $.getJSON("getPlayersInfo/"+gameid, function(data) {
    console.log(data)
    $('#you').html(data.players[0]);
    $('#opponent').html(data.players[1]);
  });
}


function status_trans(input) {
  console.log(client_status)
  console.log(input.EVENT)
  switch(client_status) {
    case ClientStatus.WAIT:
    {
      switch (input.EVENT) {
        case EventInput.ALL_IN:
          enableButton();
          client_status = ClientStatus.PREPARING;
          break;
        case EventInput.ONE_OUT:
          disableButton();
          break;
        default: break;
      }
      break;
    }
    case ClientStatus.PREPARING:
    {
      switch (input.EVENT) {
        case EventInput.ONE_OUT:
          disableButton();
          client_status = ClientStatus.WAIT;
          break;
        case EventInput.START:
          console.log('start game');
          disableButton();
          // TODO get the dir from message
          console.log(input.DIR)
          fireGame(input.DIR);
          client_status = ClientStatus.GAMING;
        default:
          break;
      }
      break;
    }
    case ClientStatus.GAMING:
    {
      switch (input.EVENT) {
        case EventInput.SCORE:
          disableButton();
          pauseGame();
          // TODO update score
          console.log(input.SCORE_MAP);
          popAlert()
          client_status = ClientStatus.PAUSE;
          
          break;
        
        case EventInput.ONE_OUT:
          disableButton();
          pauseGame();
          popAlert_redirect()
          client_status = ClientStatus.END;
          break;
        
        case EventInput.ONE_WIN:
          // pop out the result
          disableButton();
          pauseGame();
          popAlert_redirect()
          client_status = ClientStatus.END;
          break;
      }
      break;
    }
    case ClientStatus.PAUSE:
    {
      switch (input.EVENT) {
        case EventInput.START:
          fireGame(input.DIR);
          client_status = ClientStatus.GAMING;
          break;
        case EventInput.ONE_OUT:
          disableButton();
          pauseGame();
          popAlert_redirect()
          client_status = ClientStatus.END;
          break;
      }
      break;
    }
    case ClientStatus.END:
    {
      //TODO popout 
      console.log("END of the game");
      console.log("getting input of " + input);
      break;
    }
    break;
    default:
    {
      console.log("DEFAULT STATE");
    }
  }

}

function disableButton() {
  $('#ready_but').text("Click to ready");
  $('#ready_but').hide();
}

function enableButton() {
  console.log("button show!!");
  $('#ready_but').show();
}

function clickReadyButton() {
  console.log ("button clicked");
  if ($('#ready_but').text() == "Click to ready") {
    socket.send(JSON.stringify({
      TYPE: "STATE",
      STATE: 'ready',
      VAL: true,
    }));
    $('#ready_but').text("Click to unready");
  } else {
    socket.send(JSON.stringify({
      TYPE: "STATE",
      STATE: 'ready',
      VAL: false,
    }));
    $('#ready_but').text("Click to ready");
  }
}

$(document).ready(function () {
  sendRequest()

  window.setInterval(sendRequest, 1000)

  var game_id = $('#game').val()
  socket = new WebSocket('ws://' + window.location.host + '/game');

  var d = new Date();

  socket.onmessage = function(e) {
      var data = jQuery.parseJSON(e.data)
      handle(data);
  }

  socket.onopen = function() {
    $('#ready_but').click(clickReadyButton);
    disableButton();
    client_status = ClientStatus.WAIT;
  }
  
  socket.onclose = function() {
    socket.close();
  }

  // Ready button intialization

// send the pad info to server
});

});

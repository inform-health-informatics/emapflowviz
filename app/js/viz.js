const bedmoves = [];

function runWebsockets() {
    if ("WebSocket" in window) {
        var ws = new WebSocket("ws://localhost:80/ws");
        ws.onopen = function() {
            console.log("Sending websocket data");
            ws.send("Hello From Client");
        };
        ws.onmessage = function(e) {
            let msg = JSON.parse(e.data)
            // alert(e.data);
            bedmoves.push(msg);
            console.log(bedmoves);
        };
        ws.onclose = function() {
            console.log("Closing websocket connection");
        };
    } else {
        alert("WS not supported, sorry!");
    }
}
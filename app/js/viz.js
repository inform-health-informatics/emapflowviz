// deployment on the GAE
// const WEBSOCKET_SERVER = "ws://172.16.149.155:5901/ws"
// local development within docker
const WEBSOCKET_SERVER = "ws://localhost:5901/ws"
console.log('WEBSOCKET running on ' + WEBSOCKET_SERVER)
const bedmoves = [];


function runWebsockets() {
    if ("WebSocket" in window) {
        var ws = new WebSocket(WEBSOCKET_SERVER);
        ws.onopen = function() {
            console.log("Sending websocket data");
            ws.send("Hello From Client");
        };
        ws.onmessage = function(e) {
            let msg = JSON.parse(e.data)
            // alert(e.data);
            bedmoves.push(msg);
            console.log(bedmoves);
            d3.select("#viz_inspect")
                .selectAll("p")
                .data(bedmoves)
                .enter()
                .append("p")
                // .text("foobar");
                .text(function(d) { return (d); });
        };
        ws.onclose = function() {
            console.log("Closing websocket connection");
        };
    } else {
        alert("WS not supported, sorry!");
    }
}

window.onload = function main () {
    // table inspect
    d3.select("#viz_inspect")
        .selectAll("p")
        .data(bedmoves)
        .enter()
        .append("p")
        // .text("foobar");
        .text(function(d) { return (d); });
}

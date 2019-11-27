// deployment on the GAE
const pts = [];
console.log(this.WEBSOCKET_SERVER);
var value_as_number = 100;

// =====================
// set up variables etc.
// =====================

const margin = {top: 40, right: 40, bottom: 40, left: 40},
    padding = {top: 60, right: 60, bottom: 60, left: 60},
    outerWidth = 960,
    outerHeight = 500,
    innerWidth = outerWidth - margin.left - margin.right,
    innerHeight = outerHeight - margin.top - margin.bottom,
    width = innerWidth - padding.left - padding.right,
    height = innerHeight - padding.top - padding.bottom;

// copied from Bostock's path demo
// this just creates an empty data set with all the values set to 100
// TODO n creates the 'x' axis: need to switch to using dates and times
const n = 50,
    data = d3.range(n).map(d => 100);

const x = d3.scaleLinear()
    .domain([0, n - 1])
    .range([0, width]);

const y = d3.scaleLinear()
    .domain([0, 150])
    .range([height, 0]);

const line = d3.line()
    .x(function(d, i) { return x(i); })
    .y(function(d, i) { return y(d); });

const connection = new WebSocket(WEBSOCKET_SERVER);
// debugging : temporary empty connection to avoid page errors
// var connection = function () {};
connection.onopen = function() {
    console.log('>>> opened: websocket connection to ' + WEBSOCKET_SERVER)
}

connection.onclose = function() {
    console.log('>>> closed: websocket connection to ' + WEBSOCKET_SERVER)
}

connection.onmessage = function(event) {
    let newData = JSON.parse(
        JSON.parse(event.data)
        );
    console.log(newData);
    // let updateObject = map_data2pts(newData);
    pts.push(newData);
    value_as_number = newData.value_as_number;
    console.log(value_as_number);
    // updatePts(updateObject, pts);
    updateTable();
    // updateViz();
}

// test function to print the original patient load
function updateTable () {

    // console.log('sfsg: inside update table');
    let dd = pts.sort(function(a,b) {
        let aa = a.visit_detail_id;
        let bb = b.visit_detail_id;
        return aa < bb ? +1 : aa > bb ? -1 : 0;
    }).slice(0,10);
    console.log(dd);
    
    d3.select("#viz_inspect").select("table")

        .selectAll("tr")
            // .data(dd).enter()
            // .append("tr")
            .data(dd, function(i) {return i.visit_detail_id;})
            .join(
                enter => enter.append("tr"),
                update => update,
                exit => exit.remove()
            )

        .selectAll("td")
            .data(function(d) { return d3.values(d); }).enter()
            .append("td")
            .text(function(d) { return (d); }) // ;
}

// =================================================================
// the d3 functions need to run in here else there is nothing to see
// =================================================================
window.onload = function main () {

// from the realtime example
    
// table inspect
d3.select("#viz_inspect")
    .append("table");

// D3 set-up
// set up svg to hold viz with margin transform
const svg = d3.select("#viz").append("svg")
    .attr("width", outerWidth)
    .attr("height", outerHeight)

const g = svg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


g.append("defs").append("clipPath")
    .attr("id", "clip")
  .append("rect")
    .attr("width", width)
    .attr("height", height);

// hide x-axis since you still need to work out the scale
// g.append("g")
//     .attr("class", "axis axis--x")
//     .attr("transform", "translate(0," + y(0) + ")")
//     .call(d3.axisBottom(x));

g.append("g")
    .attr("class", "axis axis--y")
    .call(d3.axisLeft(y));

g.append("g")
    .attr("clip-path", "url(#clip)")
  .append("path")
    .datum(data)
    .attr("class", "line")
  .transition()
    .duration(500)
    .ease(d3.easeLinear)
    .on("start", tick);

// table inspect
d3.select("#viz_inspect")
    .selectAll("p")
    .data(pts)
    .enter()
    .append("p")
    // .text("foobar");
    .text(function(d) { return (d); });
}
// end main
console.log("end main: so far so good");

// this runs the animation and defines what happens with each browser frame refresh
function tick() {
    // Push a new data point onto the back.

    data.push(value_as_number);
    // data.push(random());
    // Redraw the line.
    d3.select(this)
        .attr("d", line)
        .attr("transform", null);
    // Slide it to the left.
    d3.active(this)
        .attr("transform", "translate(" + x(-1) + ",0)")
        .transition()
        .on("start", tick);
    // Pop the old data point off the front.
    data.shift();
}


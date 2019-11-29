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

d3.select("#svg1").style("width", (width+margin.left+margin.right)+"px");

// node parameters (for groups above)
const radius = 5,
    node_padding = 1, // Space between nodes
    cluster_padding = 5; // Space between nodes in different stages

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

// Group coordinates and meta info.
// these will be represented as 'nodes'
let top_row = height*1/4
let middle_row = height*2/4
let bottom_row = height*3/4
let left_col = width*1/4
let middle_col = width*2/4
let right_col = width*3/4

const groups = {
    "TRIAGE": { x: middle_col, y: middle_row, color: "#FAF49A", cnt: 0, fullname: "TRIAGE" },
    "DIAGNOSTICS": { x: middle_col, y: top_row, color: "#FAF49A", cnt: 0, fullname: "DIAGNOSTICS" },
    "UTC": { x: left_col, y: top_row, color: "#BEE5AA", cnt: 0, fullname: "UTC" },
    "RAT": { x: left_col, y: middle_row, color: "#BEE5AA", cnt: 0, fullname: "RAT" },
    "MAJORS": { x: right_col, y: middle_row, color: "#93D1BA", cnt: 0, fullname: "MAJORS" },
    "RESUS": { x: right_col, y: bottom_row, color: "#79BACE", cnt: 0, fullname: "RESUS" },
    "OTHER": { x: left_col, y: bottom_row, color: "#FAF49A", cnt: 0, fullname: "OTHER" },
    "PAEDS": { x: middle_col, y: bottom_row, color: "#BEE5AA", cnt: 0, fullname: "PAEDS" },
};


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
    // function should update the data that d3 accesses
    let newData = JSON.parse(
        JSON.parse(event.data)
        );
    console.log(newData);

    // pts.push(newData);
    updatePts(newData, pts);
    updateTable();
    updateViz();

    value_as_number = newData.value_as_number;
    // console.log(value_as_number);
}

function updatePts(msg, pts) {
    // push or update patient's current position
    // first insert a modifed timestamp into the msg
    msg.modified_at = Date.now();
    // alert(msg);

    // prove that you can see the new data
    // console.log("data to update");
    console.log('sfsg: updatePts running');

    // TODO generalise this since it depends on the data
    // you should add in a key to the function arguments
    // return index of patient if already in array else -1
    let pts_index = pts.findIndex( i => {return i.visit_occurrence_id === msg.visit_occurrence_id;});
    // push new patient or splice (delete and insert) as necessary
    if (pts_index === -1) {
        console.log('new patient: ' + msg.visit_occurrence_id + '; n pts = '+ pts.length);
        console.log('room_slug: ' + msg.slug_room)
        pts.push(msg);
    } else {
        console.log('old patient: ' + msg.visit_occurrence_id + '; n pts = '+ pts.length);
        console.log('room_slug: ' + msg.slug_room)
        // console.log(pts[pts_index]);
        pts.splice(pts_index, 1, msg);
        // console.log('new patient');
        // console.log(pts[pts_index]);

    };
    // TODO add in logic to remove patients from the array
}

function updateViz (update_speed=500) {
    console.log("Updating viz ...");

    // use the window namespace to access the svg from within the function
    svg = window.svg1
    //
    t = svg.transition().duration(update_speed).ease(i => i);

    
    cs = svg.selectAll( "circle" )
        .data(pts, function(d) {return d.name;})
        .join(
            enter => enter.append("circle")
                .attr( "fill", "green" ) 
                    .attr( "cx", d=>groups[d.slug_room].x + Math.random())
                    .attr( "cy", d=>groups[d.slug_room].y + Math.random())
                // .call(update => update.transition(t)
                //     .attr( "cx", d=>groups[d.slug_room].x + Math.random())
                //     .attr( "cy", d=>groups[d.slug_room].y + Math.random())
                // ),
                ,
            update => update
                .attr( "fill", "blue" ) 
                .call(update => update.transition(t)
                    .attr( "cx", d=>groups[d.slug_room].x + Math.random())
                    .attr( "cy", d=>groups[d.slug_room].y + Math.random())
                ),
            exit => exit
                .attr( "fill", "red" ) 
                .call(
                    exit => exit.transition(t)
                    )
                .remove()
        )
            .attr( "r",  d=>radius )
            .attr( "opacity", "0.1" );

}


function updateTable () {
    // test function to print the original patient load
    // function updates the data not the viz? not sure this is correct

    console.log('sfsg: updateTable running');
    // sort patients so you just see the top 10 rows
    let dd = pts.sort(function(a,b) {
        let aa = a.modified_at;
        let bb = b.modified_at;
        return aa < bb ? +1 : aa > bb ? -1 : 0;
    }).slice(0,10);
    // console.log(dd);
    
    d3.select("#viz_inspect").select("table")

        .selectAll("tr")
            // .data(dd).enter()
            // .append("tr")
            .data(dd, function(i) {return i.timestamp;})
            .join(
                enter => enter.append("tr"),
                update => update,
                exit => exit.remove()
            )

        .selectAll("td")
            // .data(function(d) { return d3.values(d); }).enter()
            .data(function(d) { return [
                d.visit_occurrence_id,
                d.timestamp_str,
                d.care_site_name,
                d.value_as_number,
                d.ward,
                d.slug_room,
                d.room,
                d.bed
                ] ; }).enter()
            .append("td")
            .text(function(d) { return (d); }) // ;
}

// =================================================================
// the d3 functions need to run in here else there is nothing to see
// =================================================================
window.onload = function main () {
// D3 set-up
// this function initially draws the viz
    
// table inspect : 2nd div on page
d3.select("#viz_inspect")
    .append("table");

// main viz set up
window.svg1 = d3.select("#viz1").append("svg")
    .attr("width", outerWidth)
    .attr("height", outerHeight)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// Group name labels
svg1.selectAll('.grp')
.data(d3.keys(groups))
.join("text")
    .attr("class", "grp")
    .attr("text-anchor", "middle")
    .attr("x", d => groups[d].x)
    .attr("y", d => groups[d].y+30)
    .text(d => groups[d].fullname);

// Group counts
svg1.selectAll('.grpcnt')
    .data(d3.keys(groups))
    .join("text")
        .attr("class", "grpcnt")
        .attr("text-anchor", "middle")
        .attr("x", d => groups[d].x)
        .attr("y", d => groups[d].y+50)
        .text(d => groups[d].cnt);

// set up svg to hold viz with margin transform
const svg2 = d3.select("#viz2").append("svg")
    .attr("width", outerWidth)
    .attr("height", outerHeight)

const g2 = svg2.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


g2.append("defs").append("clipPath")
    .attr("id", "clip")
  .append("rect")
    .attr("width", width)
    .attr("height", height);

// hide x-axis since you still need to work out the scale
// g.append("g")
//     .attr("class", "axis axis--x")
//     .attr("transform", "translate(0," + y(0) + ")")
//     .call(d3.axisBottom(x));

g2.append("g")
    .attr("class", "axis axis--y")
    .call(d3.axisLeft(y));

g2.append("g")
    .attr("clip-path", "url(#clip)")
  .append("path")
    .datum(data)
    .attr("class", "line")
  .transition()
    .duration(500)
    .ease(d3.easeLinear)
    .on("start", tick);

}
// end main
console.log("end main: so far so good");

function tick() {
    // this runs the animation and defines what happens with each browser frame refresh
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

    svg1.selectAll('.grpcnt').text(d => groups[d].cnt);
}


// Force to increment nodes to groups.
function forceCluster() {
  const strength = .15;
  let nodes;

  function force(alpha) {
    const l = alpha * strength;
    for (const d of nodes) {
      d.vx -= (d.x - groups[d.group].x) * l;
      d.vy -= (d.y - groups[d.group].y) * l;
    }
  }
  force.initialize = _ => nodes = _;

  return force;
}



// Force for collision detection.
function forceCollide() {
  const alpha = 0.2; // fixed for greater rigidity!
  const padding1 = padding; // separation between same-color nodes
  const padding2 = cluster_padding; // separation between different-color nodes
  let nodes;
  let maxRadius;

  function force() {
    const quadtree = d3.quadtree(nodes, d => d.x, d => d.y);
    for (const d of nodes) {
      const r = d.r + maxRadius;
      const nx1 = d.x - r, ny1 = d.y - r;
      const nx2 = d.x + r, ny2 = d.y + r;

      quadtree.visit((q, x1, y1, x2, y2) => {
      
        if (!q.length) do {
          if (q.data !== d) {
            const r = d.r + q.data.r + (d.group === q.data.group ? padding1 : padding2);
            let x = d.x - q.data.x, y = d.y - q.data.y, l = Math.hypot(x, y);
            if (l < r) {
              l = (l - r) / l * alpha;
              d.x -= x *= l, d.y -= y *= l;
              q.data.x += x, q.data.y += y;
            }
          }
        } while (q = q.next);
        return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
      });
    }
  }

  force.initialize = _ => maxRadius = d3.max(nodes = _, d => d.r) + Math.max(padding1, padding2);

  return force;
}

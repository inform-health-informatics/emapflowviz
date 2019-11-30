// deployment on the GAE
const pts = [];
const people = {};
// console.log(this.WEBSOCKET_SERVER);
var value_as_number = 100;

// =====================
// set up variables etc.
// =====================
// node parameters (for groups above)
const radius = 5,
    node_padding = 1, // Space between nodes
    cluster_padding = 5; // Space between nodes in different stages

const margin = {top: 40, right: 40, bottom: 40, left: 40},
    padding = {top: 60, right: 60, bottom: 60, left: 60},
    outerWidth = 960,
    outerHeight = 500,
    innerWidth = outerWidth - margin.left - margin.right,
    innerHeight = outerHeight - margin.top - margin.bottom,
    width = innerWidth - padding.left - padding.right,
    height = innerHeight - padding.top - padding.bottom;

const svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.select("#chart").style("width", (width+margin.left+margin.right)+"px");

// set up the initial svg object
d3.select("#chart").style("width", (width+margin.left+margin.right)+"px");
d3.select("#svg1").style("width", (width+margin.left+margin.right)+"px");
d3.select("#svg2").style("width", (width+margin.left+margin.right)+"px");

// Group coordinates and meta info.
// these will be represented as 'nodes'
let top_row = height*1/4
let middle_row = height*2/4
let bottom_row = height*3/4
let left_col = width*1/4
let middle_col = width*2/4
let right_col = width*3/4

const groups = {
    "TRIAGE": { x: middle_col, y: middle_row, color: "blue", cnt: 0, fullname: "TRIAGE" },
    "DIAGNOSTICS": { x: middle_col, y: top_row, color: "#FAF49A", cnt: 0, fullname: "DIAGNOSTICS" },
    "UTC": { x: left_col, y: top_row, color: "purple", cnt: 0, fullname: "UTC" },
    "RAT": { x: left_col, y: middle_row, color: "black", cnt: 0, fullname: "RAT" },
    "MAJORS": { x: right_col, y: middle_row, color: "red", cnt: 0, fullname: "MAJORS" },
    "RESUS": { x: right_col, y: bottom_row, color: "red", cnt: 0, fullname: "RESUS" },
    "OTHER": { x: left_col, y: bottom_row, color: "green", cnt: 0, fullname: "OTHER" },
    "PAEDS": { x: middle_col, y: bottom_row, color: "pink", cnt: 0, fullname: "PAEDS" },
};



// ============================================================================
// Functions
// ============================================================================
const pts_initial = d3.csv("static/data/pts_initial.csv");
console.log(pts_initial);
res = pts_initial.then(function(data) {
    // Consolidate stages by pid.
    // The data file is one row per stage change.
    data.forEach(d => {
        if (d3.keys(people).includes(d.person_id+"")) {
            people[d.person_id+""].push(d);
        } else {
            people[d.person_id+""] = [d];
        }
    });
    console.log(people);
    var nodes = d3.keys(people).map(function(d) {
        
        // Initialize coount for each group.
        groups[people[d][0].group].cnt += 1;
        
        return {
            id: "node"+d,
            x: groups[people[d][0].group].x + Math.random(),
            y: groups[people[d][0].group].y + Math.random(),
            r: radius,
            color: groups[people[d][0].group].color,
            group: people[d][0].group,
            // timeleft: people[d][0].duration,
            istage: 0,
            stages: people[d]
        };
    });
    console.log(nodes);

    // Circle for each node.
    const circle = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .join("circle")
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("fill", d => d.color);
    
    // Ease in the circles.
    circle.transition()
      .delay((d, i) => i * 5)
      .duration(800)
      .attrTween("r", d => {
        const i = d3.interpolate(0, d.r);
        return t => d.r = i(t);
      });

    // Group name labels
    svg.selectAll('.grp')
      .data(d3.keys(groups))
      .join("text")
          .attr("class", "grp")
          .attr("text-anchor", "middle")
          .attr("x", d => groups[d].x)
          .attr("y", d => groups[d].y+30)
          .text(d => groups[d].fullname);
          
    // Group counts
    svg.selectAll('.grpcnt')
      .data(d3.keys(groups))
      .join("text")
          .attr("class", "grpcnt")
          .attr("text-anchor", "middle")
          .attr("x", d => groups[d].x)
          .attr("y", d => groups[d].y+50)
          .text(d => groups[d].cnt);

    
    // Forces
    const simulation = d3.forceSimulation(nodes)
        .force("x", d => d3.forceX(d.x))
        .force("y", d => d3.forceY(d.y))
        .force("cluster", forceCluster())
        .force("collide", forceCollide())
        .alpha(.09)
        .alphaDecay(0);

    // Adjust position of circles.
    simulation.on("tick", () => {    
        circle
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .attr("fill", d => groups[d.group].color);
        });

    // Make time pass. Adjust node stage as necessary.
    function timer() {
    
        nodes.forEach(function(o,i) {
            o.timeleft -= 1;
            if (o.timeleft == 0 && o.istage < o.stages.length-1) {
                // Decrease counter for previous group.
                groups[o.group].cnt -= 1;
                
                // Update current node to new group.
                o.istage += 1;
                o.group = o.stages[o.istage].grp;
                o.timeleft = o.stages[o.istage].duration;
                
                // Increment counter for new group.
                groups[o.group].cnt += 1;
            }
        });
        
        // Increment time.
        // time_so_far += 1;
        // d3.select("#timecount .cnt").text(Date.now());
        
        // Update counters.
        svg.selectAll('.grpcnt').text(d => groups[d].cnt);
        
        // Do it again.
        d3.timeout(timer, 20);
        
    } // @end timer()
    
        
    // Start things off after a few seconds.
    d3.timeout(timer, 2000);
});

console.log(people);
console.log(">>> finished with pts_initial promise")
// Create node data.
// console.log(nodes)

// function updatePts(msg, pts) {
//     // push or update patient's current position
//     // first insert a modifed timestamp into the msg
//     msg.modified_at = Date.now();

//     // TODO generalise this since it depends on the data
//     // return index of patient if already in array else -1
//     let pts_index = pts.findIndex( i => {return i.person_id === msg.person_id;});
//     // push new patient or splice (delete and insert) as necessary
//     if (pts_index === -1) {
//         console.log('new patient: ' + msg.person_id + '; n pts = '+ pts.length);
//         console.log('room_slug: ' + msg.slug_room)
//         pts.push(msg);
//     } else {
//         console.log('old patient: ' + msg.person_id + '; n pts = '+ pts.length);
//         console.log('room_slug: ' + msg.slug_room)
//         pts.splice(pts_index, 1, msg);

//     };
//     // TODO add in logic to remove patients from the array
// }

// function updateViz (update_speed=500) {
//     console.log("Updating viz ...");

//     // use the window namespace to access the svg from within the function
//     this_svg = svg1
//     //
//     t = this_svg.transition().duration(update_speed).ease(i => i);

    
//     cs = this_svg.selectAll( "circle" )
//         .data(pts, function(d) {return d.person_id;})
//         .join(
//             enter => enter.append("circle")
//                 .attr( "fill", d=>groups[d.group].color) 
//                     .attr( "id", d=>d.person_id)
//                     .attr( "cx", d=>groups[d.group].x + Math.random())
//                     .attr( "cy", d=>groups[d.group].y + Math.random())
//                 // .call(update => update.transition(t)
//                 //     .attr( "cx", d=>groups[d.group].x + Math.random())
//                 //     .attr( "cy", d=>groups[d.group].y + Math.random())
//                 // ),
//                 ,
//             update => update
//                 .attr( "fill", d=>groups[d.group].color ) 
//                 .call(update => update.transition(t)
//                     .attr( "cx", d=>groups[d.group].x)
//                     .attr( "cy", d=>groups[d.group].y)
//                 )
//                 ,
//             exit => exit
//                 .attr( "fill", d=>groups[d.group].color ) 
//                 .call(
//                     exit => exit.transition(t)
//                     )
//                 .remove()
//         )
//             .attr( "r",  d=>radius )
//             .attr( "opacity", "0.1" );

//         simulation = d3.forceSimulation(pts)
//             .force("x", d => d3.forceX(d.x))
//             .force("y", d => d3.forceY(d.y))
//             .force("cluster", forceCluster())
//             .force("collide", forceCollide())
//             .alpha(.09);

// }


// function updateTable () {
//     // test function to print the original patient load
//     // function updates the data not the viz? not sure this is correct

//     console.log('sfsg: updateTable running');
//     // sort patients so you just see the top 10 rows
//     let dd = pts.sort(function(a,b) {
//         let aa = a.modified_at;
//         let bb = b.modified_at;
//         return aa < bb ? +1 : aa > bb ? -1 : 0;
//     }).slice(0,10);
//     // console.log(dd);
    
//     d3.select("#viz_inspect").select("table")

//         .selectAll("tr")
//             // .data(dd).enter()
//             // .append("tr")
//             .data(dd, function(i) {return i.timestamp;})
//             .join(
//                 enter => enter.append("tr"),
//                 update => update,
//                 exit => exit.remove()
//             )

//         .selectAll("td")
//             // .data(function(d) { return d3.values(d); }).enter()
//             .data(function(d) { return [
//                 d.visit_occurrence_id,
//                 d.timestamp_str,
//                 d.care_site_name,
//                 d.value_as_number,
//                 d.ward,
//                 d.slug_room,
//                 d.room,
//                 d.bed
//                 ] ; }).enter()
//             .append("td")
//             .text(function(d) { return (d); }) // ;
// }
// // ============================================================================
// // WEBSOCKETS
// // ============================================================================

// const connection = new WebSocket(WEBSOCKET_SERVER);
// connection.onopen = function() {
//     console.log('>>> opened: websocket connection to ' + WEBSOCKET_SERVER)
// }

// connection.onclose = function() {
//     console.log('>>> closed: websocket connection to ' + WEBSOCKET_SERVER)
// }

// connection.onmessage = function(event) {
//     // function should update the data that d3 accesses
//     console.log(event.data);
//     let newData = JSON.parse(
//         JSON.parse(event.data)
//         );
//     // console.log(newData);

//     // pts.push(newData);
//     updatePts(newData, pts);
//     updateTable();
//     updateViz();

//     value_as_number = newData.value_as_number;
//     // console.log(value_as_number);
// }

// // =================================================================
// // Build d3 functions 
// // =================================================================
// // First SVG SVG1
// // =================================================================

// // D3 set-up
// // this function initially draws the viz

// // table inspect : 2nd div on page
// d3.select("#viz_inspect")
//     .append("table");

// // main viz set up
// svg1 = d3.select("#viz1").append("svg")
//     .attr("width", outerWidth)
//     .attr("height", outerHeight)
//   .append("g")
//     .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// var cs = svg1.append("g")
//     .selectAll("circle")
//     .data(pts)
//     .join("circle")
//     .attr("cx", d => d.x)
//     .attr("cy", d => d.y)
//     .attr("fill", d => d.color);

// // Ease in the circles.
// cs.transition()
//     .delay((d, i) => i * 5)
//     .duration(800)
//     .attrTween("r", d => {
//     const i = d3.interpolate(0, d.r);
//     return t => d.r = i(t);
//     });
    
// // Forces
// var simulation = d3.forceSimulation(pts)
//     .force("x", d => d3.forceX(d.x*10))
//     .force("y", d => d3.forceY(d.y*100))
//     .force("charge", d3.forceManyBody().strength(-60))
//     // .force("cluster", forceCluster())
//     // .force("collide", forceCollide())
//     .alpha(.09)
//     .alphaDecay(0.1);

// simulation.on("tick", function() {
//     cs
//         .attr("cx", d => d.x)
//         .attr("cy", d => d.y)
//         .attr("fill", d => groups[d.group].color);

// });



// // Group name labels
// svg1.selectAll('.grp')
// .data(d3.keys(groups))
// .join("text")
//     .attr("class", "grp")
//     .attr("text-anchor", "middle")
//     .attr("x", d => groups[d].x)
//     .attr("y", d => groups[d].y+30)
//     .text(d => groups[d].fullname);



// ============================================================================
// FORCES
// ============================================================================

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
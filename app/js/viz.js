// Arrays
const people = {};
const msgs = [];
var nodes =[];

// Tuning
const timer_loop_delay = 10;
let time_so_far = 0;
let time_sim;
let earliest_bed_visit;
let n_discharges = 0;

// force tuning
// increment nodes toward groups
const strength = 1.75;

// Node size and spacing.
const radius = 5,
	  padding = 1, // Space between nodes
      cluster_padding = 5; // Space between nodes in different stages

// files and servers
const initial_csv = "static/data/pts_initial.csv";
const connection = new WebSocket(WEBSOCKET_SERVER);

// date and time formatting
const options1 = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: "numeric" };
const dateTimeFormat = new Intl.DateTimeFormat('en-GB', options1);

    
// SVG prep
// Dimensions of chart.
const margin = { top: 20, right: 20, bottom: 20, left: 20 },
      width = 900 - margin.left - margin.right,
      height = 360 - margin.top - margin.bottom; 



// Group coordinates and meta info.
// these will be represented as 'nodes'
let top_row = height*1/4
let middle_row = height*2/4
let bottom_row = height*3/4
let left_col = width*1/4
let middle_col = width*2/4
let right_col = width*3/4

const groups = {
    "TRIAGE": { position: 1,  color: "green", cnt: 0, fullname: "TRIAGE" },
    "DIAGNOSTICS": { position: 2,  color: "#FAF49A", cnt: 0, fullname: "DIAGNOSTICS" },
    "UTC": { position: 3,  color: "purple", cnt: 0, fullname: "UTC" },
    "RAT": { position: 4,  color: "blue", cnt: 0, fullname: "RAT" },
    "MAJORS": { position: 5,  color: "red", cnt: 0, fullname: "MAJORS" },
    "RESUS": { position: 6,  color: "red", cnt: 0, fullname: "RESUS" },
    "OTHER": { position: 7,  color: "orange", cnt: 0, fullname: "OTHER" },
    "PAEDS": { position: 8,  color: "pink", cnt: 0, fullname: "PAEDS" },
    // HOSP visit ended
    "DC": { position: 9,  color: "black", cnt: 0, fullname: "DC" },
    // PLACEHOLDER FOR NEW MESSAGES
    "NEWBIE": { position: 10,  color: "white", cnt: 0, fullname: "NEWBIE" },
};

// set up positions of wards
// TODO convert to circle
function degrees2radians (x) { return (x%360)/360 * 2 * Math.PI; }
function x_polar (x, radius) { return width/2 +  radius * Math.cos(degrees2radians(x))}
function y_polar (y, radius) { return height/2 + radius * Math.sin(degrees2radians(y))}
// TODO need error checking to make sure that positions are unique and sequential
const group_ring_radius = Math.min(width,height)/2 * 0.70;
let label_offset = group_ring_radius * 1.5;
let cnt_offset = group_ring_radius * 1.3;
let positions = d3.keys(groups).length;

d3.keys(groups).map(e => {groups[e].x = x_polar(groups[e].position/positions*360, group_ring_radius)})
d3.keys(groups).map(e => {groups[e].y = y_polar(groups[e].position/positions*360, group_ring_radius)})

d3.keys(groups).map(e => {groups[e].label_x = x_polar(groups[e].position/positions*360, label_offset)})
d3.keys(groups).map(e => {groups[e].label_y = y_polar(groups[e].position/positions*360, label_offset)})

d3.keys(groups).map(e => {groups[e].cnt_x = (groups[e].label_x)})
d3.keys(groups).map(e => {groups[e].cnt_y = (groups[e].label_y+20)})
// d3.keys(groups).map(e => {groups[e].cnt_x = x_polar(groups[e].position/positions*360, cnt_offset)})
// d3.keys(groups).map(e => {groups[e].cnt_y = y_polar(groups[e].position/positions*360, cnt_offset)})

// set up the simulation object
const simulation = d3.forceSimulation()
    .force("x", d => d3.forceX(d.x))
    .force("y", d => d3.forceY(d.y))
    .force("cluster", forceCluster())
    .force("collide", forceCollide())
    .alpha(.09)
    .alphaDecay(0)
    .on("tick", ticked);

// ======================
// SVG DIV
// ======================

d3.select("#chart").style("width", (width+margin.left+margin.right)+"px");
const svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var cs = svg.append("g")
    .attr("id", "bubbles")
    .selectAll("circle");

// ======================
// Table DIV
// ======================
// table inspect : 2nd div on page
d3.select("#viz_inspect").style("width", (width+margin.left+margin.right)+"px");
const mytable = d3.select("#viz_inspect").append("table");

initial_pt_load();

// ========================================
// UPDATES based on messages from websocket
// ========================================

function restart () {

}

// ============================================================================
// WEBSOCKETS
// ============================================================================

connection.onopen = function() {
    console.log('>>> opened: websocket connection to ' + WEBSOCKET_SERVER)
}

connection.onclose = function() {
    console.log('>>> closed: websocket connection to ' + WEBSOCKET_SERVER)
}

connection.onmessage = function(event) {
    // function should update the data that d3 accesses
    let d = JSON.parse(
        JSON.parse(event.data)
        );
    d.modified_at = Date.now();
    d.modified_at_str = dateTimeFormat.format(Date.now());
    d.source = 'websocket';
    msgs.push(d);
    console.log('new websocket message');
    console.log(d);

    // update the people dictionary of arrays
    if (d3.keys(people).includes(d.person_id+"")) {
        people[d.person_id+""].push(d);
    } else {
        people[d.person_id+""] = [d];
    };

    // update nodes separately because it is possible that the person has already left
    let nodes_idx = nodes.findIndex( i => {return i.person_id === d.person_id;});

    // push new patient or splice (delete and insert) as necessary
    if (nodes_idx === -1) {
        console.log('new patient: ' + d.person_id + '; nodes = '+ nodes.length);
        // TODO create a fake stage called NEWBIE and use this / or just create a colour and set a timer
        nodes.push(make_node_from_people(d.person_id, source='websocket'));
    } else {
        console.log('old patient: ' + d.visit_occurrence_id + '; nodes = '+ nodes.length);
        n_stages = nodes[nodes_idx].stages.length
        // TODO join on pp_parent_fact
        if (nodes[nodes_idx]
                .stages.map(d => d.pp_parent_fact_id)
                .includes(d.pp_parent_fact_id)) {
            console.log("!!! fact already exists");
        } else {
            console.log(">>> new fact");
            console.log('updating nodes_idx: ' + nodes_idx);
            // // testing 
            // console.log("before foo: " + nodes[nodes_idx].foo)
            // nodes[nodes_idx].foo = Date.now();
            // console.log("after foo: " + nodes[nodes_idx].foo)
            // update the hospital end date 
            nodes[nodes_idx].hosp_visit_end = d.hosp_visit_end;
            console.log("before stages length: " + nodes[nodes_idx].stages.length)
            nodes[nodes_idx].stages.push(d);
            console.log("after stages length: " + nodes[nodes_idx].stages.length)
            // TODO update the prev stage duration so that it closes
            // nodes[nodes_idx].stages[n_stages-2].
            // TODO update the prev stage bed duration

        }

        cs = cs.data(nodes, d => d.person_id);
        cs.exit()
            .attr("fill", "black")
            .remove();
        cs = cs.enter().append("circle")
              .attr("id", d => d.person_id)
              .attr("cx", d => d.x)
              .attr("cy", d => d.y)
              .attr("fill", d => d.color)
              .attr("r", 5)
              .merge(cs);

        simulation.nodes(nodes);
        simulation.alpha(0.01).velocityDecay(0.5).restart();


    };

    updateTable(mytable);

    value_as_number = d.value_as_number;
    // console.log(value_as_number);
}
// =========.
// Load data.
// =========.
// asynchronous promise 

async function initial_pt_load () {
    const data = await d3.csv(initial_csv);
    // Once data is loaded...

    
    // Define when sim starts based on the earliest time in the data
    earliest_bed_visit = d3.min(data, function(d) {
        return Date.parse(d.bed_visit_start);
      });
    time_sim = earliest_bed_visit;
    
    // Consolidate stages by pid. (person_id)
    // The data file is one row per stage change.
    data.forEach(d => {
        d.modified_at = Date.now();
        d.source = initial_csv;
        d.modified_at_str = dateTimeFormat.format(Date.now());
        if (d3.keys(people).includes(d.person_id+"")) {
            people[d.person_id+""].push(d);
        } else {
            people[d.person_id+""] = [d];
        }
    });
    
    // Create node data.
    nodes = d3.keys(people).map(function(d) {
        
        // Initialize coount for each group.
        groups[people[d][0].grp].cnt += 1;
        return make_node_from_people(d, source='csv')
    });
    // to permit inspection during debugging
    window.nodes_inspect = nodes;
    
    
    // t = svg.transition().duration(1500).ease(i => i);
    cs = cs.data(nodes, d => d.person_id);
    cs.exit()
        .transition()
        .duration(1000)
        .attr("fill", "black")
        .remove();
    cs = cs.enter().append("circle")
          .attr("id", d => d.person_id)
          .attr("cx", d => d.x)
          .attr("cy", d => d.y)
          .attr("r", 5)
          .attr("fill", d => d.color)
          .merge(cs);

    // to permit inspection during debugging
    window.cs_inspect = cs;
    
    // Ease in the circles.
    // cs.transition()
    //   .delay((d, i) => i * 5)
    //   .duration(800)
    //   .attrTween("r", d => {
    //     const i = d3.interpolate(0, d.r);
    //     return t => d.r = i(t);
    //   });

    // Group name labels
    svg.selectAll('.grp')
      .data(d3.keys(groups))
      .join("text")
          .attr("class", "grp")
          .attr("text-anchor", "middle")
          .attr("x", d => groups[d].label_x)
          .attr("y", d => groups[d].label_y)
          .text(d => groups[d].fullname);
          
    // Group counts
    svg.selectAll('.grpcnt')
      .data(d3.keys(groups))
      .join("text")
          .attr("class", "grpcnt")
          .attr("text-anchor", "middle")
          .attr("x", d => groups[d].cnt_x)
          .attr("y", d => groups[d].cnt_y)
          .text(d => groups[d].cnt);

    simulation.nodes(nodes);
    simulation.alpha(0.01).velocityDecay(0.5).restart();

    // Start things off after a few seconds.
    // !!! and because timer then calls itself then this is actually the start of a loop
    d3.timeout(timer, 2000);
   
    
}

function timer() {

    cs = cs.data(nodes, d => d.person_id);
    cs.exit()
        .attr("fill", "black")
        .remove();
    cs = cs.enter().append("circle")
          .attr("id", d => d.person_id)
          .attr("cx", d => d.x)
          .attr("cy", d => d.y)
          .attr("fill", d => d.color)
          .attr("r", 5)
          .merge(cs);

    // update simulation with new nodes every second (even though they're
    // already in the nodes array)
    if (time_so_far % 1000 === 0) {

        simulation.nodes(nodes);
        simulation.alpha(0.09).restart();
    };
    
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
        };
        if (!(o.hosp_visit_end === null) & time_sim > o.hosp_visit_end & o.group != "DC") {
            groups[o.group].cnt -= 1;
            o.group = "DC";
            groups[o.group].cnt += 1;
            // console.log(o.id_node + " has left the building");
            
        }
    });
    nodes = nodes.filter(function(el) { return el.group != "DC"; });
    // for debugging; gets these local variables visible
    nodes_inspect = nodes;
    cs_inspect = cs;

    
    // Increment time.
    time_so_far += 1;
    time_sim += 60000; // microseconds hence 1 minute per loop
    d3.select("#timenow .cnt").text(dateTimeFormat.format((time_sim)));
    // d3.select("#timenow .cnt").text(dateTimeFormat.format((Date.now())));
    d3.select("#timecount .cnt").text(time_so_far);
    
    // Update counters.
    svg.selectAll('.grpcnt').text(d => groups[d].cnt);
    
    // Do it again.
    // !!! see comment above; this is a loop
    d3.timeout(timer, timer_loop_delay);
    
} // @end timer()

// =========================
// FUNCTIONS and methods etc
// =========================

function make_node_from_people (d, source) {
    // expects a key from the people dictionary
    // returns a dictionary organised for the node
    return {
        person_id: d,
        x: groups[people[d][0].grp].x + Math.random(),
        y: groups[people[d][0].grp].y + Math.random(),
        r: radius,
        color: groups[people[d][0].grp].color,
        group: people[d][0].grp,
        timeleft: people[d][0].bed_los,
        istage: 0,
        stages: people[d],
        hosp_visit_start: Date.parse(people[d][0].hosp_visit_start),
        hosp_visit_end: Date.parse(people[d][0].hosp_visit_end),
        source: source
    }
}


// =========================
// FUNCTIONS for FORCES
// =========================


// what to do with each tick
function ticked () {
    cs
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("fill", d => groups[d.group].color);
        // .attr("fill", function(d) {
        //     if (d.source === "websocket") {
        //         "white"
        //     } else {
        //         groups[d.group].color
        //     }
        // })
}

// Force to increment nodes to groups.
function forceCluster() {
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


function updateTable (_table) {
    // test function to print the original patient load
    // function updates the data not the viz? not sure this is correct

    // console.log('sfsg: updateTable running');
    let dd = msgs.slice(-10).reverse();
    // console.log(dd);
    
    // d3.select("#viz_inspect").select("table")
   _table

        .selectAll("tr")
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
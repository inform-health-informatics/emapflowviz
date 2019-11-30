const people = {};
let time_so_far = 0;
let time_sim;
let earliest_bed_visit;
const n_discharges = 0;


const options1 = { year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: "numeric" };
const dateTimeFormat = new Intl.DateTimeFormat('en-GB', options1);

// Node size and spacing.
const radius = 5,
	  padding = 1, // Space between nodes
      cluster_padding = 5; // Space between nodes in different stages
    
// Dimensions of chart.
const margin = { top: 20, right: 20, bottom: 20, left: 20 },
      width = 900 - margin.left - margin.right,
      height = 360 - margin.top - margin.bottom; 

const svg = d3.select("#chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.select("#chart").style("width", (width+margin.left+margin.right)+"px");



// Group coordinates and meta info.
// these will be represented as 'nodes'
let top_row = height*1/4
let middle_row = height*2/4
let bottom_row = height*3/4
let left_col = width*1/4
let middle_col = width*2/4
let right_col = width*3/4

const groups = {
    "TRIAGE": { x: middle_col, y: middle_row, color: "green", cnt: 0, fullname: "TRIAGE" },
    "DIAGNOSTICS": { x: middle_col, y: top_row, color: "#FAF49A", cnt: 0, fullname: "DIAGNOSTICS" },
    "UTC": { x: left_col, y: top_row, color: "purple", cnt: 0, fullname: "UTC" },
    "RAT": { x: left_col, y: middle_row, color: "blue", cnt: 0, fullname: "RAT" },
    "MAJORS": { x: right_col, y: middle_row, color: "red", cnt: 0, fullname: "MAJORS" },
    "RESUS": { x: right_col, y: bottom_row, color: "red", cnt: 0, fullname: "RESUS" },
    "OTHER": { x: left_col, y: bottom_row, color: "orange", cnt: 0, fullname: "OTHER" },
    "PAEDS": { x: middle_col, y: bottom_row, color: "pink", cnt: 0, fullname: "PAEDS" },
    // HOSP visit ended
    "DC": { x: right_col+100 , y: middle_row, color: "black", cnt: 0, fullname: "DC" },
};

// Load data.
// const stages = d3.tsv("data/stages.tsv", d3.autoType);
// const stages = d3.csv("data/stages.csv");
// const stages = d3.csv("static/data/adt4d3.csv");
const stages = d3.csv("static/data/pts_initial.csv");



// Once data is loaded...
stages.then(function(data) {
    
    // Define when sim starts based on the earliest time in the data
    earliest_bed_visit = d3.min(data, function(d) {
        return Date.parse(d.bed_visit_start);
      });
    console.log(earliest_bed_visit);
    time_sim = earliest_bed_visit;
    
    // Consolidate stages by pid. (person_id)
    // The data file is one row per stage change.
    data.forEach(d => {
        if (d3.keys(people).includes(d.person_id+"")) {
            people[d.person_id+""].push(d);
        } else {
            people[d.person_id+""] = [d];
        }
    });
    
    // Create node data.
    var nodes = d3.keys(people).map(function(d) {
        
        // Initialize coount for each group.
        groups[people[d][0].grp].cnt += 1;
        
        return {
            id: "node"+d,
            x: groups[people[d][0].grp].x + Math.random(),
            y: groups[people[d][0].grp].y + Math.random(),
            r: radius,
            color: groups[people[d][0].grp].color,
            group: people[d][0].grp,
            timeleft: people[d][0].bed_los,
            istage: 0,
            stages: people[d],
            hosp_visit_start: Date.parse(people[d][0].hosp_visit_start),
            hosp_visit_end: Date.parse(people[d][0].hosp_visit_end)
        }
    });
    // to permit inspection during debugging
    window.nodes_inspect = nodes;
    
    
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
          .attr("y", d => groups[d].y+50)
          .text(d => groups[d].fullname);
          
    // Group counts
    svg.selectAll('.grpcnt')
      .data(d3.keys(groups))
      .join("text")
          .attr("class", "grpcnt")
          .attr("text-anchor", "middle")
          .attr("x", d => groups[d].x)
          .attr("y", d => groups[d].y+70)
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
        // circle
        //     .attr("fill", "blue");
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
            };
            if (time_sim > o.hosp_visit_end & o.group != "DC") {
                groups[o.group].cnt -= 1;
                o.group = "DC";
                groups[o.group].cnt += 1;
                console.log(o.id + " has left the building");
                
            }
        });

//         circle.selectAll("circle")
//         .data(nodes, function(d) {return d.id;})
//         .join(
//             enter => enter.append("circle")
//                 // .attr( "fill", d=>groups[d.grp].color) 
//                     // .attr( "id", d=>d.person_id)
//                     // .attr( "cx", d=>groups[d.grp].x + Math.random())
//                     // .attr( "cy", d=>groups[d.grp].y + Math.random())
//                 ,
// //             update => update
// //                 .attr( "fill", d=>groups[d.grp].color ) 
// //                 .call(update => update.transition(t)
// //                     .attr( "cx", d=>groups[d.grp].x)
// //                     .attr( "cy", d=>groups[d.grp].y)
// //                 )
//             exit => exit
//                 .attr( "fill", "green" ) 
//                 .remove()
//         );
        
        // Increment time.
        time_so_far += 1;
        time_sim += 60000;
        d3.select("#timenow .cnt").text(dateTimeFormat.format((time_sim)));
        // d3.select("#timenow .cnt").text(dateTimeFormat.format((Date.now())));
        d3.select("#timecount .cnt").text(time_so_far);
        
        // Update counters.
        svg.selectAll('.grpcnt').text(d => groups[d].cnt);
        
        // Do it again.
        d3.timeout(timer, 20);
        
    } // @end timer()

    
    // Start things off after a few seconds.
    d3.timeout(timer, 2000);
   
    
});





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

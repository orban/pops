//For the purpose of inspection
//--------------------------------
var vertices, edges, vertex_list, edge_list;
var svg, force, labels;
var arrow_list
//-------------------------------

//d3.json("/data/simple.json", function(data) {
d3.json("/data/nba_social_graph.json", function(data) {
    vertices = data.vertices;    
    edges = data.edges;

    var width = 1000;
    var height = 600;
    var colors = d3.scale.category20c();
    svg = d3.select('body').append('svg')
        .attr('width', width)
        .attr('height', height);

    var w = 960,
        h = 500
        markerWidth = 20,
        markerHeight = 20,
        cRadius = 5, // play with the cRadius value
        refX = cRadius *2  + markerWidth/2, //where connecting the vertex.
        refY = 0//Math.sqrt(cRadius),
        drSub = cRadius + refY;

    force = d3.layout.force().size([width, height])
        .nodes(vertices)
        .links(edges).linkDistance(150)
        .charge(-300).friction(.5).gravity(.2)
        .on("tick", tick)
        .start();
        // .linkStrength( function(link, index) {
        //     return link.strength;
        // })

    // arrow marker
    svg.append("svg:defs").selectAll("marker")
        .data("endMarker")
        .enter().append("svg:marker")
        .attr("id", "endMarker")
        // .attr("viewBox", "0 0 0 0") 
        .attr("refX", refX)
        .attr("refY", refY)
        .attr("markerWidth", markerWidth)
        .attr("markerHeight", markerHeight)
        .attr("orient", "auto")
        .append("svg:path")
        .attr("d", "M-50, -20L20, 0L0, 5") //M-5,-10L20,0L0,10")
        .attr("fill", colors(3))
        .attr("stroke", colors(3));

    vertex_list = svg.selectAll("circle.vertex").data(vertices).enter().append("circle")
        .attr("class", "vertex")
        .attr("r", function(v) { 
                return v.node_size;
            })
        .style("stroke", function(v) { 
                return v.node_color;
            })
        .style("fill", function(v) { 
                return v.node_color;
            })
    ;

    // Append the labels to each group
    // labels = svg.selectAll("svg.vertex_text").data(vertices).enter().append("svg:text")
    //     .attr('class', 'vertex_text')
    //     .text(function(d) {return d.name;})
    //     .style("fill", "black").style("font-family", "Serif").style("font-size", 10);

    edge_list = svg.selectAll("line.edge").data(edges).enter()
        .append("line")
        .attr("class", "edge")
        .style('stroke', colors(1));
//        .style('marker-end', 'url(#endMarker)');

    // Action
    function tick() {
        // labels
        //     .attr('text_anchor', 'start')
        //     .attr("x", function(v) { 
        //         return v.x;
        //     })
        //     .attr("y", function(v) {
        //         return v.y; 
        //     });
        vertex_list
            .attr("cx", function(v) { 
                return v.x;
            })
            .attr("cy", function(v) {
                return v.y; 
            });
        edge_list
            .attr("x1", function(e) { 
                return e.source.x; })
            .attr("y1", function(e) { 
                return e.source.y; })
            .attr("x2", function(e) { 
                return e.target.x; })
            .attr("y2", function(e) { 
                return e.target.y; });
    }
    vertex_list.call(force.drag);

});


//For the purpose of inspection
//--------------------------------
var vertices, edges, vertex_list, edge_list;
var svg, force, labels;
var arrow_list
//-------------------------------

//d3.json("/data/simple.json", function(data) {
d3.json("/static/data/simple.json", function(data) {
    vertices = data.vertices;    
    edges = data.edges;
	
    var width = $("#box2").width();
    var height = $("#box2").height();
    var colors = d3.scale.category20c();

    svg = d3.select('#box2').append('svg')
        .attr('width', width)
        .attr('height', height);	

    var markerWidth = 25,
        markerHeight = 10,
        cRadius = 50, // play with the cRadius value
        refX = cRadius *2  + markerWidth/2, //where connecting the vertex.
        refY = 0//Math.sqrt(cRadius),
        drSub = cRadius + refY;

    force = d3.layout.force().size([width, height])
        .nodes(vertices)
        .links(edges).linkDistance(200)
        .charge(-200).friction(.8).gravity(.01)
        // .linkStrength( function(link, index) {
        //     return link.strength;
        // })
        .on("tick", tick)
        .start();

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
        .attr("d", "M-50, -20L20, 0L0, 5")
        .attr("fill", colors(3))
        .attr("stroke", colors(3));

    // var path = svg.append("svg:g").selectAll("path")
    //     .data(force.links())
    //     .enter().append("svg:path")
    //     .attr("class", "path")
    //     .attr("d", "M0,-5L10,0L0,5")
    //     .attr("fill", "none")
    //     .attr("stroke", colors(4))
    //     .attr("marker-end", "url(#endMarker)");


    vertex_list = svg.selectAll("circle.vertex").data(vertices).enter().append("circle")
        .attr("class", "vertex")
        .attr("r", cRadius)
        .style("stroke", colors(2))
        .style("fill", colors(2));

    // Append the labels to each group
    labels = svg.selectAll("svg.vertex_text").data(vertices).enter().append("svg:text")
        .attr('class', 'vertex_text')
        .text(function(d) {return d.name;})
        .style("fill", "black").style("font-family", "Serif").style("font-size", 10);

    edge_list = svg.selectAll("line.edge").data(edges).enter()
        .append("line")
        .attr("class", "edge")
        .style('stroke', colors(1))
        .style('marker-end', 'url(#endMarker)');

    // // Arrows
    // arrow_list = svg.selectAll("line.arrow").data(edges).enter()
    //     .append('svg:path')
    //     .attr('d', 'M0,-5L10,0L0,5')
    //     .append('svg:marker')
    //     .attr('id', 'end-arrow')
    //     .attr('viewBox', '0 -5 10 10')
    //     .attr('refX', 6)
    //     .attr('markerWidth', 10)
    //     .attr('markerHeight', 10)
    //     .attr('orient', 'auto')
    //     .attr('fill', 'black')
    //     .append("line")
    //     .attr("class", "edge")
    //     .style('stroke', colors(1))
    //     .style('marker-end', 'url(#end-arrow)');

    // var path = svg.append("svg:g").selectAll("path")
    //     .data(force.links())
    //     .enter().append("svg:path")
    //     .attr("class", 'path')
    //     .attr('marker-end', "url(#endMarker)"
    //     .append("svg:marker")
    //     .attr("id", String)
    //     .attr("viewBox", "0 0 10 10")
    //     .attr("refX", 10)
    //     .attr("refY", 50)
    //     .attr("markerWidth", 20)
    //     .attr("markerHeight", 20)
    //     .attr("orient", "auto");

    // Action
    function tick() {
        labels
            .attr('text_anchor', 'start')
            .attr("x", function(v) { 
                return v.x - cRadius/3;
            })
            .attr("y", function(v) {
                return v.y + cRadius/4; 
            });
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


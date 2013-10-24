//For the purpose of inspection
//--------------------------------
var vertices, edges, vertex_list, edge_list;
var svg, force, labels;
var arrow_list
//-------------------------------

//d3.json("/data/simple.json", function(data) {
d3.json("/static/data/hist_cr.json", function(data) {

    vertices = data.vertices;    
    edges = data.edges;
	
    var width = $("#box2").width();
    var height = $("#box2").height();
    var colors = d3.scale.category20c();

    svg = d3.select('#box2').append('svg')
        	.attr('width', width)
        	.attr('height', height);	

    var rect_x= 0,
        rect_y= 0,
    	rect_width = 50,
    	rect_height= 30,
		rect_rx = rect_width * 0.1, 
		rect_ry = rect_height * 0.1; 
		
	var markerWidth = 25,
		markerHeight = 10,
	   	cRadius = 50, // play with the cRadius value
	   	refX = .7*(rect_width+rect_height) //where connecting the vertex.
	    refY = 0 //Math.sqrt(cRadius),
	    drSub = cRadius + refY;

    force = d3.layout.force().size([width, height])
        .nodes(vertices)
        .links(edges).linkDistance(300)
        .charge(-300).friction(.1).gravity(.01).linkStrength(1)
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

// svg:rect x="0" y="0" width="0" height="0" rx="0" ry="0"

    vertex_list = svg.selectAll("rect.vertex").data(vertices).enter().append("rect")
        .attr("class", "vertex")
	    .attr('width', rect_width)
	    .attr('height', rect_height)
		.attr('rx', rect_rx)
		.attr('ry', rect_ry)
        .style("stroke", 'white')//colors(2))
        .style("fill", 'white');//colors(2));

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

    // Action
    function tick() {
        labels
            .attr('text_anchor', 'start')
            .attr("x", function(v) { 
                return v.x - rect_width/3;
            })
            .attr("y", function(v) {
                return v.y + rect_height/8; 
            });
        vertex_list
            .attr("x", function(v) { 
                return v.x - rect_width/2;
            })
            .attr("y", function(v) {
                return v.y - rect_height/2; 
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


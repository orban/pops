// =====================================================
// =====================================================

//app for the MATCHUPS tab
var matchup_app = function() {

    var matchup = angular.module('matchup', ['ui.bootstrap']);

    matchup.controller('ctrl_choose_matchup', function($scope, $http) {

        $(document).ajaxComplete(function() {
            
            $scope.submit = function() {
                var _route = "/analyze_matchup";
                var _json;
                
                var _chosen_date = $('#datepicker').val();
                var _games = schedule_2014[_chosen_date];
                var game;
	            var _selected = parseInt(/^[0-9]+/g.exec($scope.selectedValues));

                game = _games[_selected];

                console.log(game);

                //send data to the server for analysis
                _json = JSON.stringify(game);

                $.ajax({
                    type:"POST",
                    url: _route,
                    data: {"data": _json},
                    beforeSend: function(){
                        $("#status").text("  "+"...ANALYZING...");
                    },
                    ajaxError: function(e) {
                        console.log(e);
                        $("#status").text("");
                    },
                    success: function(response) {
                        var data_home = response['data_home'];
                        var data_visitor = response['data_visitor'];

                        $("#status").text("");
                        console.log(data_home);
                        console.log(data_visitor);
                        // d3.select("#svg-matchup").select('svg').remove();
                        // drawDag(data, "#svg-matchup");
                    }});

            };

            //control for clicking on the games
	        $scope.selectionsChanged = function(){
	            // console.log($scope.selectedValues);
	        };
        });
    });

   matchup.controller('tabCtrl', function($scope) {

       $scope.showHome = function() {
           console.log('clicking home tab');
       };
       $scope.showVisitor = function() {
           console.log('clicking visitor tab');
       };

       $scope.navType = 'pills';
   });                      

};


function drawDag(data, box) {
    var vertices = data.vertices;
    var edges = data.edges;
	
    var width = $(box).width();
    var height = $(box).height();

    var colors = d3.scale.category20c();
    var nodeColor = "rgb(220,220,220)";
    var textColor = "rgb(204,204,204)"; 

    var causalNodeColor = "rgb(95,158,160)";
    var internalNodeColor = "rgb(120,120,120)"; 
    var terminalNodeColor = "rgb(70,130,180)";

    var causalNodeSize = 1;
    var internalNodeSize = 1;
    var terminalNodeSize = 1;

    var causalStartingX = width * 0
    var internalStartingX = width * 1/2;
    var terminalStartingX = width * 1;
    var causalStartingY = height * 1;
    var internalStartingY = height * 1/2;
    var terminalStartingY = height * 0;

    var foci = [{x: causalStartingX, y: causalStartingY}, 
                {x: internalStartingX, y: internalStartingY}, 
                {x: terminalStartingX, y: terminalStartingY}];
    
    var causalNodeCharge = 3.0;
    var internalNodeCharge = 1.0;
    var terminalNodeCharge = 3.0;

    var posEdgeColor = "rgb(205,133,63)";
    var negEdgeColor = "rgb(238,232,170)";

    var rect_width = 50;
    var	rect_height= 25;
	var rect_rx = rect_width * 0.1;
    var rect_ry = rect_height * 0.1; 
		
	var markerWidth = 25;
	var markerHeight = 10;
	var refX = .5 *(rect_width+rect_height) + 20; //where to connect to the node
	var refY = 0;

    var svg = d3.select(box).append('svg')
        .attr('width', width)
        .attr('height', height);	

    // creating markers
    svg.append("svg:defs").selectAll("marker")
        .data(["posMarker", "negMarker"])
        .enter().append("svg:marker")
        .attr("id", String)
        .attr("refX", refX)
        .attr("refY", refY)
        .attr("markerWidth", markerWidth)
        .attr("markerHeight", markerHeight)
        .attr("orient", "auto")
        .append("svg:path")
        .attr("d", "M0, -5L10, 0L0, 3")
        .attr("fill", function(m) {
            return (m === "posMarker") ? posEdgeColor : negEdgeColor;
        })
        .attr("stroke", function(m) {
            return (m === "posMarker") ? posEdgeColor : negEdgeColor;
        });

    var force = d3.layout.force().size([width, height])
        .nodes(vertices)
	    .charge(function(v) {
            var _charge = -200;
            if (v.type === "causal") {
                _charge = _charge * causalNodeCharge;
            } else if (v.type === "internal") {
                _charge = _charge * internalNodeCharge;
            } else {
                _charge = _charge * terminalNodeCharge;
            };
            return _charge;
        })
        .gravity(.08)
        .links(edges)
        .linkDistance(function(link) {
            _scale = Math.max(1.1, Math.min(link.strength, 2))
            return link.dist * _scale;
        })
        .linkStrength( function(link, index) {
            _strength = Math.max(0.4, Math.min(link.strength, 1))
            return _strength;
        })
        .alpha(.01).friction(.2)
        .on("tick", tick)
        .start();

    var drag = force.drag()
        .on("dragstart", dragstart);

    // edges
    var edge_list = svg.selectAll("line.edge").data(edges).enter()
        .append("line")
        .attr("class", "edge")
        .style("stroke-width", function(e) {
            var _strokeWidth = 1.3;
            _strokeWidth = 0.2 + _strokeWidth * e.strength * 3.5;
            _strokeWidth = Math.min(5, _strokeWidth);
            return String(_strokeWidth) + "px";
        })
        .style('stroke', function(e){
            return (e.sign === 1) ? posEdgeColor: negEdgeColor;
        })
        .style('marker-end', function (e) {
            return (e.sign === 1) ? "url(#posMarker)" : "url(#negMarker)";
        });

    // vertices
    var vertex_list = svg.selectAll("rect.vertex").data(force.nodes()).enter().append("rect")
        .attr("class", "vertex")
	    .attr('width', function(v) {
            var _size;
            if (v.type === "causal") {
                _size = (10 + (v.name.length) * 8) * causalNodeSize;
            }
            else if (v.type === "internal") {
                _size = (10 + (v.name.length) * 8) * internalNodeSize;
            }
            else {
                _size = (10 + (v.name.length) * 8) * terminalNodeSize;
            };
            return _size;
        })  
	    .attr('height', rect_height)
		.attr('rx', rect_rx)
		.attr('ry', rect_ry)
        .attr("x", function(v) { 
            var _startingX;
            if (v.type === "causal") {
                _startingX = causalStartingX;
            } else if (v.type === "internal") {
                _startingX = internalStartingX;
            } else {
                _startingX = terminalStartingX;
            };
            return _startingX;
        })
        .attr("y", function(v) { 
            var _startingY;
            if (v.type === "causal") {
                _startingY = causalStartingY;
            } else if (v.type === "internal") {
                _startingY = internalStartingY;
            } else {
                _startingY = terminalStartingY;
            };
            return _startingY;
        })
        .style("stroke", function(node) {
            var _color;
            if (node.type === "causal") {
                _color = causalNodeColor
            } else if (node.type === "internal") {
                _color = internalNodeColor;
            } else {
                _color = terminalNodeColor;
            };
            return _color;
        })
        .style("fill", function(node) {
            var _color;
            if (node.type === "causal") {
                _color = causalNodeColor
            } else if (node.type === "internal") {
                _color = internalNodeColor;
            } else {
                _color = terminalNodeColor;
            };
            return _color;
        })
        .call(drag);


    // append the labels to each group
    var labels = svg.selectAll("svg.vertex_text").data(vertices).enter().append("svg:text")
        .attr('class', 'vertex_text')
        .text(function(d) {return d.name;})
        .call(drag)
        .attr("x", function(v) { 
            var _startingX;
            if (v.type === "causal") {
                _startingX = causalStartingX;
            } else if (v.type === "internal") {
                _startingX = internalStartingX;
            } else {
                _startingX = terminalStartingX;
            };
            return _startingX;
        })
        .attr("y", function(v) { 
            var _startingY;
            if (v.type === "causal") {
                _startingY = causalStartingY;
            } else if (v.type === "internal") {
                _startingY = internalStartingY;
            } else {
                _startingY = terminalStartingY;
            };
            return _startingY;
        })
        .style("fill", "black").style("font-family", "Monospace")
        .style("font-size", function(node) {
            var _size = 12;
            if (node.type === "causal") {
                _size = _size * causalNodeSize;
            } else if (node.type === "internal") {
                _size = _size * internalNodeSize;
            } else {
                _size = _size * terminalNodeSize;
            };
            return _size;
        });

    // Action
    function tick() {
        labels
            .attr('text_anchor', 'start')
            .attr("x", function(v) { 
                return v.x - rect_width/3;
            })
            .attr("y", function(v) {
                return v.y + rect_height/8 + 1; 
            });
        vertex_list
            .attr("x", function(v) { 
                return v.x - rect_width/2;
            })
            .attr("y", function(v) {
                return v.y - rect_height/2; 
            });

        var k = 30;
        vertex_list.forEach(function(o, i) {
            var focus;
            if (o.type === "causal") {
                focus = foci[0];
            } else if (o.type === "internal") {
                focus = foci[1];
            } else {
                focus= foci[2];
            };
            o.y += (focus.y - o.y) * k;
            o.x += (focus.x - o.x) * k;
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
    };

    function dragstart(d) {
        d.fixed = true;
        d3.select(this).classed("fixed", true);
    };

};

// =====================================================================
// =====================================================================


// ---------------------------------------
// Getting the necessary data from files
// ---------------------------------------
var schedule_2014 = {};
var graph_data_home;
var graph_data_visitor;

$.getJSON("/static/data/2014_schedule.json", function(json) {
    schedule_2014 = json;
});

//---------------------------
//initialize the matchup app
//---------------------------

// make the calendar 
$(document).ajaxComplete(function() {
    $(function() {
        $("#datepicker").datepicker();
    });
});

// initialize the angular app for the MATCHUP tab
matchup_app();


// // draw the dag svg
// d3.json("/static/data/matchup_cr.json", function(data) {
//     drawDag(data, "#svg-matchup");
// });



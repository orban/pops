var hist = angular.module('hist', []);

var features_dict; 
var features_selection = {};
$.getJSON("/static/data/features.json", function(json) {
    features_dict = json;
});

//write the html for the selection box
$(document).ajaxComplete(function() {
	
 	var _html = '';
	for(var k in features_dict) {
		_html += "<option value=" + k  + "ng-selected='features_selection_result." 
				 + k + "'>" +features_dict[k] + "</option>"
	};
	document.getElementById("feature_selection").innerHTML = _html;
});

//app for the EXPLORE tab
hist.controller('ctrl_feature_selection', function($scope, $http) {
    $(document).ajaxComplete(function() {
        //selection box
	$scope.selectionsChanged = function(){
	    var _selected = [];
            var _html = '';
            
	    for (var i in $scope.selectedValues){
		_selected.push(parseInt(/^[0-9]+/g.exec($scope.selectedValues[i])));
	    };
	    $scope.selection_result = [];	
	    for(var i in features_dict) {
       		if (-1 != $.inArray(parseInt(i), _selected)) {
		    $scope.selection_result.push(features_dict[i]);						
		};
	    };
            
            $("#selected-features").html('');
            for (var i in $scope.selection_result){
                feature = $scope.selection_result[i];
                _html = _html + '<li>' + feature + '</li>';
            };
            _html = '<ol>' + _html + '</ol>';
            _html = 
                $("#selected-features").html(_html);
	};

        //submit for analysis
        $scope.submit = function(){
	    var _selected = [];
	    for (var i in $scope.selectedValues){
		_selected.push(parseInt(/^[0-9]+/g.exec($scope.selectedValues[i])));
	    };
	    var feature_list = [];
	    for(var i in features_dict) {
       		if (-1 != $.inArray(parseInt(i), _selected)) {
		    feature_list.push(features_dict[i]);						
		};
	    };
            var _route = "/analyze_hist";
            var _json = JSON.stringify(feature_list);

            $.ajax({
                type:"POST",
                url: _route,
                data: {"data": _json},
                beforeSend: function(){
                    $("#analyzing").text("  "+"...ANALYZING...");
                },
                ajaxError: function(e) {
                    console.log(e);
                },
                success: function(response) {
                    var data = response['output'];
                    $("#analyzing").text("");
                    d3.select("svg").remove();
                    draw(data);
                }});
        };				
    });	
});

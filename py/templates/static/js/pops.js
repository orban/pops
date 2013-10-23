var app = angular.module('pops', []);

var features_dict; 
var features_selection = {};
$.getJSON("/static/data/features.json", function(json) {
    features_dict = json;
});

//wait until the data are loaded before
//executing the javascripts
$(document).ajaxComplete(function() {
	
 	var _html = '';
	for(var k in features_dict) {
		_html += "<option value=" + k  + "ng-selected='features_selection_result." 
				 + k + "'>" +features_dict[k] + "</option>"
	};
	document.getElementById("feature_selection").innerHTML = _html;
});

app.controller('controller_feature_selection', function($scope) {
	//initiating the values
	$(document).ajaxComplete(function() {
		$scope.selectionsChanged = function(){
			var _selected = [];
			for (var i in $scope.selectedValues){
				_selected.push(parseInt(/^[0-9]+/g.exec($scope.selectedValues[i])));
			};
			$scope.features_selection_result = [];	
			for(var i in features_dict) {
       			if (-1 != $.inArray(parseInt(i), _selected)) {
					$scope.features_selection_result.push(features_dict[i]);						
				};
			};
		};				
	});	
});




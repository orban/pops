

var schedule_2014 = {};
$.getJSON("/static/data/2014_schedule.json", function(json) {
    schedule_2014 = json;
});

//app for the MATCHUPS tab
var matchup_app = function() {

    var matchup = angular.module('matchup', []);
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
                        var data = response['output'];
                        $("#status").text("");
                        console.log(data);
                        // d3.select("svg").remove();
                        // draw(data);
                    }});

            };

            //control for clicking on the games
	        $scope.selectionsChanged = function(){
	            // console.log($scope.selectedValues);
	        };
        });
    });
};


$(document).ajaxComplete(function() {
    $(function() {
        $("#datepicker").datepicker();
    });
});

//initialize the matchup app
 matchup_app();
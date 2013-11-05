var matchup = angular.module('matchup', []);


var schedule_2014 = {};
$.getJSON("/static/data/2014_schedule.json", function(json) {
    schedule_2014 = json;
});

//creating the calendar
$(document).ajaxComplete(function() {
    $(function() {
        $("#datepicker").datepicker();
    });
});




//app for the MATCHUPS tab
matchup.controller('ctrl_choose_matchup', function($scope, $http) {
    $(document).ajaxComplete(function() {
        
    });
});
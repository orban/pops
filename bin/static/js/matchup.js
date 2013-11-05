var matchup = angular.module('matchup', []);

//creating the calendar
$(function() {
    $("#datepicker").datepicker();
});

//app for the MATCHUPS tab
matchup.controller('ctrl_choose_matchup', function($scope, $http) {
    $(document).ajaxComplete(function() {
        
        //binding the calendar 

        // $("#datepicker").datepicker();

	// $scope.showGame = function(){
        //     console.log($scope.text)
        // };
    });
});
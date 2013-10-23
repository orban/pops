var app = angular.module('pops', []);

function inArray(x, arr) {
  for(var i = 0; i < arr.length; i++) {
    if(x === arr[i]) return true;
  }
  return false;
}

app.controller('feature_selection', function($scope) {
   $scope.query = {
                Statuses: {
                    Draft: true,
                    Live: true,
                    Pending: true,
                    Archived: false,
                    Deleted: false
                }
            };
  $scope.selectionsChanged = function(){
    for(var key in $scope.query.Statuses) {
      $scope.query.Statuses[key] = inArray(key, $scope.selectedValues);
    }
  };
  
});
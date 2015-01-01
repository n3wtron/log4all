/**
 * Created by igor on 12/23/14.
 */
var log4all = angular.module('log4all', ["angucomplete-alt","ngAnimate"]);

log4all.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
});

log4all.controller('LogController', function ($scope, $http) {
    $scope.inError = false;

    $scope.src_query={
        page:0,
        max_result:10,
        levels:['DEBUG','WARN','INFO','ERROR'],
        sort_field:'date',
        sort_ascending:false
    };

    $scope.updateApplication = function(selected) {
        if (selected != null) {
            $scope.src_query.applications = selected.originalObject.field;
        }else{
            $scope.src_query.applications = null;
        }
    };

    $scope.updateLevel=function(level){
        var levelPos = $scope.src_query.levels.indexOf(level);
        if ( levelPos == -1) {
            $scope.src_query.levels.push(level);
        }else{
            $scope.src_query.levels.splice(levelPos,1);
        }
    };

    $scope.levelIsEnabled = function(level){
        return $scope.src_query.levels.indexOf(level)!=-1;
    };

    $scope.searchHidden = false;
    $scope.search = function () {
        $http.post('http://localhost:6543/api/logs/search', $scope.src_query).success(function (data) {
            console.log(data);
            if (data.success == false){

                $scope.inError = true;
                $scope.errorMessage = data.message;
            }else {
                $scope.inError = false;
                $scope.errorMessage = null;

                var tags = new Set();
                angular.forEach(data.result, function (log) {
                    angular.forEach(log.tags, function (key, value) {
                        tags.add(value);
                    });
                });
                $scope.tags = [];
                tags.forEach(function (tag) {
                    $scope.tags.push(tag);
                });
                $scope.src_query.tags = $scope.tags;
                $scope.logs = data.result;
            }
        });
    };
    $scope.sortResult=function(field){
        if ($scope.src_query.sort_field == field){
            $scope.src_query.sort_ascending = ! $scope.src_query.sort_ascending;
        }else{
            $scope.src_query.sort_field = field;
            $scope.src_query.sort_ascending = true;
        }
        $scope.search();
    }
});

log4all.controller('AddLogController', function ($scope, $http) {
    $scope.log={};
    $scope.setLogApplication = function(selected){
        console.log(selected);
        if (selected != null) {
            $scope.log.application = selected.originalObject.field;
        }else{
            $scope.log.application = null;
        }
    };
    $scope.addLog = function(level){
        $scope.log.level = level;
        console.log($scope.log);
        $http.post('http://localhost:6543/api/logs/add', $scope.log).success(function (data) {
            console.log(data);
            if (!data.success){
                $scope.inError = true;
                $scope.errorMessage = data.message;
            }else {
                $scope.inError = false;
                $scope.errorMessage = null;
                $('#addLogPanel').modal('hide');
            }
        });
    };
});
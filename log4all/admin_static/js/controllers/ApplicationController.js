/**
 * Created by igor on 3/11/15.
 */
Log4AllAdmin.controller('ApplicationController', function ($scope, $http, $routeParams,$interval,log4AllApplicationService) {
    $scope.application = {};

    log4AllApplicationService.get($routeParams.applicationId).then(function (data) {
        $scope.application = data;
        if ($scope.application.configuration == null) {
            $scope.application.configuration = {};
        }
        $scope.changeConfiguration("DEBUG");
    },function(error){
        alert(error);
    });

    $scope.currentConfiguration = {};
    $scope.changeConfiguration = function (level) {
        $scope.currentConfigurationLevel = level;
        if ($scope.application.configuration == null || !(level in $scope.application.configuration)) {
            $scope.currentConfiguration = {
                archive: 30,
                delete: 90
            };
            $scope.application.configuration[level] = $scope.currentConfiguration;
        } else {
            $scope.currentConfiguration = $scope.application.configuration[level];
        }
    };

    $scope.updateApplication = function () {
        $scope.result = {};
        console.log($scope.application);
        log4AllApplicationService.update($routeParams.applicationId,$scope.application).then(function (data) {
            if (data['success']) {
                $scope.result.success = true;
                $scope.result.message = "Updated";
                $interval(function () {
                    $scope.result = null;
                }, 3000);
            } else {
                $scope.result.success = false;
                $scope.result.message = "Not Updated. Error:" + data['message'];
            }
        },function(error){
            alert(error);
        });
    };

});
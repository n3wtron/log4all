/**
 * Created by igor on 3/11/15.
 */
Log4AllAdmin.controller('GroupController', function ($scope, $http, $routeParams, $interval, log4AllGroupService, log4AllAuthService) {
    $scope.group = {};

    log4AllGroupService.get($routeParams.groupId).then(function (data) {
        $scope.group = data;
    });

    $scope.updateGroup = function () {
        $scope.result = {};
        console.log($scope.group);
        log4AllGroupService.update($routeParams.groupId, $scope.group).then(function (data) {
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
        });
    };

    $scope.updateGroupPermission = function (permission) {
        if ($scope.group.permissions == undefined) {
            $scope.group.permissions = [permission];
        } else {
            var permPos = $scope.group.permissions.indexOf(permission);
            if (permPos > -1) {
                $scope.group.permissions.splice(permPos, 1);
            } else {
                $scope.group.permissions.push(permission);
            }
        }
    };

    $scope.groupHasPermission = function (permission) {
        if ($scope.group.permissions == undefined) {
            return false;
        } else {
            return $scope.group.permissions.indexOf(permission) > -1;
        }
    };

    angular.element(document).ready(function () {
        log4AllAuthService.getPermissions().then(function (data) {
            $scope.permissions = data;
            console.log($scope.permissions);
        }, function (error) {
            alert("Cannot retreive permissions")
        });
    });

});
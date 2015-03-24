/**
 * Created by igor on 3/11/15.
 */
Log4AllAdmin.controller('UserController', function ($scope, $http, $routeParams, $location, $interval, log4AllGroupService, log4AllUserService) {
    $scope.user = {};

    log4AllUserService.get($routeParams.userId).then(function (data) {
        $scope.user = data;
    }, function (error) {
        alert(error);
    });


    $scope.updateUser = function () {
        $scope.result = {};
        console.log($scope.user);
        log4AllUserService.update($routeParams.userId, $scope.user).then(function (data) {
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
        }, function (error) {
            alert(error);
        });
    };

    $scope.addUserToGroup = function (groupName) {
        if ($scope.user.groups == undefined) {
            $scope.user.groups = [groupName];
        } else {
            var pos = $scope.user.groups.indexOf(groupName);
            if (pos > -1) {
                $scope.user.groups.splice(pos, 1);
            } else {
                $scope.user.groups.push(groupName);
            }
        }
    };

    $scope.userHasGroup = function (groupName) {
        if ($scope.user.groups == undefined){
            return false;
        }else {
            return $scope.user.groups.indexOf(groupName) > -1;
        }
    };

    log4AllGroupService.getAll().then(function (groups) {
        $scope.groups = groups;
    }, function (error) {
        alert(error);
    });


});
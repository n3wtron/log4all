/**
 * Created by igor on 3/11/15.
 */

Log4AllAdmin.controller('LoginController', function ($scope, $http, localStorageService, log4AllAuthService) {
    $scope.auth = {};
    $scope.login = function () {
        log4AllAuthService.login($scope.auth).then(function (data) {
            if (data.success) {
                localStorageService.set('jwt_token', data.token)
            } else {
                alert(data.message);
                $scope.auth.password = null;
            }
        }, function (error) {
            alert(error);
        });
    };

    $scope.logout = function () {
        localStorageService.remove('jwt_token');
    };

});
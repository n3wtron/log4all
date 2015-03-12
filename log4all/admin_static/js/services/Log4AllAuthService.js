/**
 * Created by igor on 3/12/15.
 */
log4AllAdminServiceModule.service('log4AllAuthService', ['$http', '$q', function ($http, $q) {
    var login = function (userAuth) {
        var deferedResponse = $q.defer();
        $http.post('/api/auth/login', userAuth).success(function (data) {
            deferedResponse.resolve(data);
        }).error(function (data, status) {
            deferedResponse.reject("Status:" + status + " :" + data);
        });
        return deferedResponse.promise;
    };

    var getPermissions=function(){
        var deferedResponse = $q.defer();
        $http.get('/api/auth/permissions').success(function (data) {
            deferedResponse.resolve(data);
        }).error(function (data, status) {
            deferedResponse.reject("Status:" + status + " :" + data);
        });
        return deferedResponse.promise;
    };
    return {
        'login':login,
        'getPermissions':getPermissions
    }
}]);
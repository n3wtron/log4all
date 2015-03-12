/**
 * Created by igor on 3/11/15.
 */
log4AllAdminServiceModule.service('log4AllUserService', ['$http', '$q', function ($http, $q) {

    var getAll = function () {
        var deferedResult = $q.defer();
        $http.get('/api/users').success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data, status) {
            deferedResult.reject("Error status:" + status + " :" + data);
        });
        return deferedResult.promise;
    };
    var get = function (userId) {
        var deferedResult = $q.defer();
        $http.get('/api/user/' + userId).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data, status) {
            deferedResult.reject("Error status:" + status + " :" + data);
        });
        return deferedResult.promise;
    };
    var deleteUser = function (userId) {
        var deferedResult = $q.defer();
        $http.delete('/api/user/' + userId).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };
    var add = function (user) {
        var deferedResult = $q.defer();
        $http.put('/api/user', user).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };
    var update = function (userId, user) {
        var deferedResult = $q.defer();
        $http.post('/api/user/' + userId, user).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };

    return {
        'getAll': getAll,
        'get': get,
        'delete': deleteUser,
        'add': add,
        'update': update
    }

}]);
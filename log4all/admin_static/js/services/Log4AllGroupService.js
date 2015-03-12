/**
 * Created by igor on 3/11/15.
 */
log4AllAdminServiceModule.service('log4AllGroupService', ['$http', '$q', function ($http, $q) {

    var getAll = function () {
        var deferedResult = $q.defer();
        $http.get('/api/groups').success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data, status) {
            deferedResult.reject("Error status:" + status + " :" + data);
        });
        return deferedResult.promise;
    };
    var get = function (groupId) {
        var deferedResult = $q.defer();
        $http.get('/api/group/' + groupId).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data, status) {
            deferedResult.reject("Error status:" + status + " :" + data);
        });
        return deferedResult.promise;
    };
    var deleteGroup = function (groupId) {
        var deferedResult = $q.defer();
        $http.delete('/api/group/' + groupId).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };
    var add = function (group) {
        var deferedResult = $q.defer();
        $http.put('/api/group', group).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };
    var update = function (groupId, group) {
        var deferedResult = $q.defer();
        $http.post('/api/group/' + groupId, group).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };

    return {
        'getAll': getAll,
        'get': get,
        'delete': deleteGroup,
        'add': add,
        'update': update
    }

}]);
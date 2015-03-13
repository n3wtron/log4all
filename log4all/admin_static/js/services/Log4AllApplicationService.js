/**
 * Created by igor on 3/11/15.
 */
log4AllAdminServiceModule.service('log4AllApplicationService', ['$http', '$q', function ($http, $q) {

    var getAll = function () {
        var deferedResult = $q.defer();
        $http.get('/api/applications').success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data, status) {
            deferedResult.reject("Error status:" + status + " :" + data);
        });
        return deferedResult.promise;
    };
    var get = function (applicationId) {
        var deferedResult = $q.defer();
        $http.get('/api/application/' + applicationId).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data, status) {
            deferedResult.reject("Error status:" + status + " :" + data);
        });
        return deferedResult.promise;
    };
    var deleteApplication = function (applicationId) {
        var deferedResult = $q.defer();
        $http.delete('/api/application/' + applicationId).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };
    var add = function (application) {
        var deferedResult = $q.defer();
        $http.put('/api/application', application).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };
    var update = function (applicationId, application) {
        var deferedResult = $q.defer();
        $http.post('/api/application/' + applicationId, application).success(function (data) {
            deferedResult.resolve(data);
        }).error(function (data) {
            deferedResult.reject(data);
        });
        return deferedResult.promise;
    };

    return {
        'getAll': getAll,
        'get': get,
        'delete': deleteApplication,
        'add': add,
        'update': update
    }

}]);
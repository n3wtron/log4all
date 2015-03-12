/**
 * Created by igor on 3/11/15.
 */
Log4AllAdmin.controller('ApplicationsController', function ($scope, $http, $location) {
    $scope.application = {};

    $scope.addApplication = function () {
        $http.put(getApiUrl($location,'applications/add'), $scope.application).success(function (data) {
            console.log(data);
            if (data['success']) {
                updateApplications();
                $location.path('applications/' + data.application['_id']);
                $('#addLogModal').modal('hide');
            }
        });
    };

    $scope.deleteApplication = function (applicationId) {
        $http.delete(getApiUrl($location,'application/delete?id=' + applicationId)).success(function (data) {
            updateApplications();
        });
    };

    function updateApplications() {
        $http.get(getApiUrl($location,'applications')).success(function (data) {
            $scope.applications = data;
        });
    }

    updateApplications();
});

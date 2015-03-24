/**
 * Created by igor on 3/11/15.
 */
Log4AllAdmin.controller('ApplicationsController', function ($scope, $http, $location, log4AllApplicationService) {
    $scope.application = {};

    $scope.addApplication = function () {
        log4AllApplicationService.add($scope.application).then(function (data) {
            console.log(data);
            if (data['success']) {
                updateApplications();
                $('#addApplicationModal').modal('hide');
                $location.path('applications/' + data.application['_id']);
            }
        }, function (error) {
            alert(error);
        });
    };

    $scope.deleteApplication = function (applicationId) {
        log4AllApplicationService.delete(applicationId).then(function (data) {
            updateApplications();
        }, function (error) {
            alert(error);
        });
    };

    function updateApplications() {
        log4AllApplicationService.getAll().then(function (data) {
            $scope.applications = data;
        }, function (error) {
            alert(error);
        });
    }

    updateApplications();
});

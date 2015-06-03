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
                $location.path('applications/' + data.result['_id']);
            }
        }, function (error) {
            alert(error);
        });
    };

    $scope.openDelApplicationMdl = function(index){
        $scope.applicationToDel = index;
        $('#delApplicationMdl').modal('show');
    }

    $scope.closeDelApplicationMdl=function(){
        $('#delApplicationMdl').modal('hide');
        $scope.applicationToDel = undefined;
    }; 

    $scope.deleteApplication = function () {
        log4AllApplicationService.delete($scope.applicationToDel._id).then(function (data) {
            updateApplications();
        }, function (error) {
            alert(error);
        });
        $('#delApplicationMdl').modal('hide');
    };

    function updateApplications() {
        log4AllApplicationService.getAll().then(function (data) {
         if (data['success']) {
           $scope.applications = data['result'];
       }else{
        alert(data['message']);
    }
}, function (error) {
    alert(error);
});
    }

    updateApplications();
});

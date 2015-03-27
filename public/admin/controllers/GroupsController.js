/**
 * Created by igor on 3/11/15.
 */
Log4AllAdmin.controller('GroupsController', function ($scope, $http, $location, log4AllGroupService) {
    $scope.group = {};

    $scope.addGroup = function () {
        log4AllGroupService.add($scope.group).then(function (data) {
            if (data['success']) {
                updateGroups();
                $('#addGroupModal').modal('hide');
                $location.path('groups/' + data.result['_id']);
            }else{
				alert(data['message']);
			}
        });
    };

    $scope.deleteGroup = function (groupId) {
        log4AllGroupService.delete(groupId).then(function (data) {
            updateGroups();
        });
    };

    function updateGroups() {
        log4AllGroupService.getAll().then(function (data) {
			if (data['success']) {
            	$scope.groups = data.result;
			}else{
				alert(data['message']);
			}
        }, function (error) {
            alert(error);
        });
    }

    updateGroups();
});

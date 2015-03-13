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
                $location.path('groups/' + data.group['_id']);
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
            $scope.groups = data;
        }, function (error) {
            alert(error);
        });
    }

    updateGroups();
});

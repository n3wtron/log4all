/**
 * Created by igor on 3/11/15.
 */
Log4AllAdmin.controller('UsersController', function ($scope, $http, $location,log4AllUserService) {
    $scope.user = {};

    $scope.addUser = function () {
        log4AllUserService.add($scope.user).then(function (data) {
            if (data['success']) {
                updateUsers();
                $('#addUserModal').modal('hide');
                $location.path('users/' + data.user['_id']);
            }else{
				alert(data.message);
			}
        },function(error){
           alert(error);
        });
    };

    $scope.deleteUser = function (userId) {
        log4AllUserService.delete(userId).then(function (data) {
            updateUsers();
        },function(error){
            alert(error);
        });
    };

    function updateUsers() {
        log4AllUserService.getAll().then(function (data) {
			if (data.success){
            	$scope.users = data.result;
			}else{
				alert(data.message);
			}
        },function(error){
            alert(error);
        });
    }

    updateUsers();
});

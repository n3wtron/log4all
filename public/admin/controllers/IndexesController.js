
Log4AllAdmin.controller('IndexesController', function ($scope, $http, $location, log4AllIndexesService) {
	$scope.refreshIndexes=function(){
		log4AllIndexesService.getAll().then(function(data){
			if (!data.success){
				alert(data.message);
			}else{
				$scope.indexes = data['indexes'];
			}
		},function(error){
			alert(error);
		})};

		$scope.addIndex = function(){
			log4AllIndexesService.addIndex($scope.index).then(function(data){
				if (!data.success){
					alert(data.message);
				}else{
					$('#addIndexModal').modal('hide');
					$scope.refreshIndexes();
				}
			},function(error){alert(error);}); 
		}

		$scope.deleteIndex = function(index){
			log4AllIndexesService.deleteIndex(index).then(function(data){
				if (!data.success){
					alert(data.message);
				}else{
					$scope.refreshIndexes();
				}
			},function(error){alert(error);}); 
		};

		$scope.refreshIndexes();
	});
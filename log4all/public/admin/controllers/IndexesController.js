
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

		$scope.openDelIndexMdl = function(index){
			$scope.indexToDel = index;
			$('#delIndexMdl').modal('show');
		}

		$scope.deleteIndex = function(){
			log4AllIndexesService.deleteIndex($scope.indexToDel).then(function(data){
				if (!data.success){
					alert(data.message);
				}else{
					$scope.refreshIndexes();
				}
				$('#delIndexMdl').modal('hide');
			},function(error){alert(error);}); 
		};
		$scope.closeDelIndexMdl=function(){
			$('#delIndexMdl').modal('hide');
			$scope.indexToDel = undefined;
		};

		$scope.refreshIndexes();
	});
/**
 * Created by igor on 12/28/14.
 */
var Log4AllAdmin = angular.module('Log4AllAdmin', ['ngRoute', 'ngAnimate', 'angular-jwt', 'LocalStorageModule','Log4AllAdminServiceModule']);

Log4AllAdmin.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
});


Log4AllAdmin.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/applications', {
            templateUrl: "/public/admin_fragment/applications.html",
            controller: 'ApplicationsController'
        }).when('/applications/:applicationId', {
            templateUrl: "/public/admin_fragment/application.html",
            controller: 'ApplicationController'
        }).when('/groups/', {
            templateUrl: "/public/admin_fragment/groups.html",
            controller: 'GroupsController'
        }).when('/groups/:groupId', {
            templateUrl: "/public/admin_fragment/group.html",
            controller: 'GroupController'
        }).when('/users/', {
            templateUrl: "/public/admin_fragment/users.html",
            controller: 'UsersController'
        }).when('/users/:userId', {
            templateUrl: "/public/admin_fragment/user.html",
            controller: 'UserController'
        });
}]);

Log4AllAdmin.directive('ngEnter', function() {
        return function(scope, element, attrs) {
            element.bind("keydown keypress", function(event) {
                if(event.which === 13) {
                        scope.$apply(function(){
                                scope.$eval(attrs.ngEnter);
                        });

                        event.preventDefault();
                }
            });
        };
});

Log4AllAdmin.controller('MainController', function ($scope, localStorageService) {
    $scope.isLogged = function () {
        return localStorageService.get('jwt_token') != undefined;
    };
});

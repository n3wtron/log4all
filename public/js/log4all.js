        /**
         * Created by igor on 12/23/14.
         */

        log4AllURL = "http://localhost:9000";

        var log4all = angular.module('log4all', ["angucomplete-alt", "ngAnimate", "Log4AllServiceModule"]);

        log4all.config(function($interpolateProvider) {
            $interpolateProvider.startSymbol('{[{');
            $interpolateProvider.endSymbol('}]}');
        });

        log4all.filter('code', function() {
            return function(text) {
                if (text != undefined) {
                    return text.replace(new RegExp('\n', 'g'), '<br/>')
                } else {
                    return "";
                }
            }
        });

        log4all.filter('unsafe', function($sce) {
            return function(val) {
                return $sce.trustAsHtml(val);
            };
        });

        log4all.controller('LogController', function($scope, $location, $http, $interval, Log4AllService) {
            $scope.resultType = null;
            $scope.followLog = false;
            var tailRefresh;

            $scope.resetSearch = function() {
                if (angular.isDefined(tailRefresh)) {
                    $interval.cancel(tailRefresh);
                    tailRefresh = undefined;
                    $scope.resultType = null;
                }
                $scope.src_query = {
                    page: 0,
                    query: '',
                    max_result: 10,
                    levels: ['DEBUG', 'WARN', 'INFO', 'ERROR'],
                    sort_field: 'date',
                    sort_ascending: false
                };
                $scope.logs = [];
                $scope.resultTags = [];
            };
            $scope.resetSearch();

            // Retrieve all tags
            $scope.getTags = function() {
                $http.get(getApiUrl($location, 'tags')).success(function(data) {
                    $scope.tags = data;
                });
            };
            //$scope.getTags();

            $scope.addTagInQuery = function(tag) {
                $scope.src_query.query += " #" + tag;
            };

            $scope.addTagValueInQuery = function(tag, tagValue, searchAfter) {
                var tag_src = "#" + tag + "=" + tagValue;
                if ($scope.src_query.query.indexOf(tag_src) > 0) {
                    $scope.src_query.query = $scope.src_query.query.replace(tag_src, "");
                    $scope.src_query.query = $scope.src_query.query.replace("  ", " ");
                } else {
                    $scope.src_query.query += " " + tag_src;
                }
                if (searchAfter) {
                    $scope.search();
                }
            };

            $scope.updateApplication = function(selected) {
                if (selected != null) {
                    $scope.src_query.applications = selected.originalObject.name.split(" ");
                } else {
                    $scope.src_query.applications = [];
                }
            };

            $scope.updateLevel = function(level) {
                var levelPos = $scope.src_query.levels.indexOf(level);
                if (levelPos == -1) {
                    $scope.src_query.levels.push(level);
                } else {
                    $scope.src_query.levels.splice(levelPos, 1);
                }
            };

            $scope.levelIsEnabled = function(level) {
                return $scope.src_query.levels.indexOf(level) != -1;
            };

            $scope.searchHidden = false;
            $scope.search = function() {
                //stop tail
                if (angular.isDefined(tailRefresh)) {
                    $interval.cancel(tailRefresh);
                    tailRefresh = undefined;
                }

                Log4AllService.searchLog($scope.src_query.applications,
                    $scope.src_query.levels,
                    $scope.src_query.dt_since,
                    $scope.src_query.dt_to,
                    $scope.src_query.query,
                    $scope.src_query.page,
                    $scope.src_query.max_result,
                    $scope.src_query.sort_field,
                    $scope.src_query.sort_ascending).then(function(data) {
                    if (data.success) {
                        $scope.resultType = 'searchResult';
                        $scope.errorMessage = null;
                        $scope.logs = data.logs;
                        $scope.resultTags = data.tags;
                    } else {
                        $scope.resultType = 'error';
                        $scope.errorMessage = error;
                    }
                }, function(error) {
                    $scope.resultType = 'error';
                    $scope.errorMessage = error;
                });

            };


            $scope.tail = function() {
                $scope.tailLogs = [];
                if (angular.isDefined(tailRefresh)) {
                    return;
                }
                var tailDtTo = new Date().getTime();
                var newLog = false;
                $scope.resultType = 'tailResult';
                tailRefresh = $interval(function() {
                    if (newLog && $scope.followLog) {
                        //scroll to bottom
                        window.scrollTo(0, document.body.scrollHeight);
                    }
                    newLog = false;

                    Log4AllService.tailLog($scope.src_query.applications,
                        $scope.src_query.levels,
                        tailDtTo-1000,
                        tailDtTo,
                        $scope.src_query.query,
                        $scope.src_query.max_result,
                        $scope.src_query.sort_field,
                        $scope.src_query.sort_ascending).then(function(data) {
                        if (data.success) {
                            console.log(data)
                            //remove first 100 after 200
                            if ($scope.tailLogs.length > 200) {
                                $scope.tailLogs.splice(0, 100);
                            }
                            if (data.logs != undefined) {
                                data.logs.forEach(function(lg) {
                                    newLog = true;
                                    $scope.tailLogs.push(lg);
                                });
                            }
                            tailDtTo = new Date().getTime();
                        } else {
                            $scope.resultType = 'error';
                            $scope.errorMessage = data.message;
                            $interval.cancel(tailRefresh);
                        }
                    }, function(error) {
                        $scope.resultType = 'error';
                        $scope.errorMessage = data.message;
                        $interval.cancel(tailRefresh);
                    });
                }, 1000);
            };

            function getStack(log) {
                if (log['stack_sha'] != undefined) {
                    $http.get(getApiUrl($location, 'stack?sha=' + log['stack_sha'])).success(function(data) {
                        log['stack'] = data;
                    });
                } else {
                    log['stack'] = undefined;
                }
            }

            $scope.showDetail = function(log) {
                $scope.prevSearchHidden = $scope.searchHidden;
                $scope.searchHidden = true;
                $scope.logDetail = log;
                getStack($scope.logDetail);
                $scope.prevResultType = $scope.resultType;
                $scope.resultType = "logDetail";
            };

            $scope.closeDetail = function() {
                if ($scope.searchHidden != $scope.prevSearchHidden) {
                    $scope.searchHidden = $scope.prevSearchHidden;
                }
                $scope.resultType = $scope.prevResultType;
            };

            $scope.changePage = function(page) {
                if (page < 0) {
                    $scope.src_query.page = 0;
                } else {
                    $scope.src_query.page = page;
                }
                if ($scope.src_query.dt_since != null && $scope.src_query.dt_to != null) {
                    $scope.search();
                }
            };
            $scope.sortResult = function(field) {
                if ($scope.src_query.sort_field == field) {
                    $scope.src_query.sort_ascending = !$scope.src_query.sort_ascending;
                } else {
                    $scope.src_query.sort_field = field;
                    $scope.src_query.sort_ascending = true;
                }
                $scope.search();
            }
        });

        log4all.controller('AddLogController', function($scope, $http, $location, Log4AllService) {
            $scope.log = {};
            $scope.setLogApplication = function(selected) {
                if (selected != null) {
                    $scope.log.application = selected.originalObject.field;
                } else {
                    $scope.log.application = null;
                }
            };
            $scope.addLog = function(level) {
                $scope.log.level = level;
                Log4AllService.addLog($scope.log).then(function(data) {
                    console.log(data);
                    if (!data.success) {
                        $scope.inError = true;
                        $scope.errorMessage = data.message;
                        alert($scope.errorMessage);
                    } else {
                        $scope.inError = false;
                        $scope.errorMessage = null;
                        $('#addLogPanel').modal('hide');
                    }
                }, function(error) {
                    alert(error)
                });
            };
        });
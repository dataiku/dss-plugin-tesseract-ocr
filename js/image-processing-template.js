var app = angular.module('imageProcessingTemplate.module', []);

app.controller('ImageProcessingController', function($scope, CodeBasedEditorUtils) {
    $scope.editorOptions = CodeBasedEditorUtils.editorOptions('text/x-python', $scope)
});

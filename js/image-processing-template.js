var app = angular.module('imageProcessingTemplate.module', []);

app.controller('ImageProcessingController', function ($scope, CodeBasedEditorUtils) {
    $scope.editorOptions = CodeBasedEditorUtils.editorOptions('text/x-python', $scope)
    if (typeof $scope.config.functions_definition == 'undefined') {
        $scope.config.functions_definition = `
# Define here the different image processing python functions
# Don\'t forget to import required packages (that are in the plugin code env)
# Both input and output of these functions are numpy array image

# for example
import cv2

def thresholding(image):
    \"\"\" Set pixels to black or white based on some threshold. \"\"\"   
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def resizing(image):
    \"\"\" Rescale an image. fx and fx denote the scaling factors. \"\"\"
    return cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    
# More info here on open-cv image processing here:
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html
`
    }

    if (typeof $scope.config.pipeline_definition == 'undefined') {
        $scope.config.pipeline_definition = `
# Fill-in complete_processing with functions defined above

def complete_processing(image):
    # This function will be executed on all images in the input folder

    # add the functions you defined above here

    # for example
    image = thresholding(image)
    image = resizing(image)

    return image
`
    }
});

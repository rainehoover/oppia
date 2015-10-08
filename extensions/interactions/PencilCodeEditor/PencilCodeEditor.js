// Copyright 2014 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Directive for the PencilCodeEditor interaction.
 *
 * IMPORTANT NOTE: The naming convention for customization args that are passed
 * into the directive is: the name of the parameter, followed by 'With',
 * followed by the name of the arg.
 */
oppia.directive('oppiaInteractivePencilCodeEditor', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'interaction/PencilCodeEditor',
      controller: ['$scope', '$attrs', '$element',
          function($scope, $attrs, $element) {

        $scope.initialCode = oppiaHtmlEscaper.escapedJsonToObj(
          $attrs.initialCodeWithValue);

        var pce = new PencilCodeEmbed($element[0].children[0]);
        pce.beginLoad($scope.initialCode);
        pce.on('load', function() {
          // Hide the turtle.
          pce.setupScript([{
            code: 'ht();', type: 'text/coffeescript'
          }]);

          pce.hideToggleButton();
          pce.setEditable();
          pce.showEditor();
        });

        $scope.reset = function() {
          pce.setCode($scope.initialCode);
        };

        pce.on('execute', function() {
          // TODO(sll): Add console output as well.
          $scope.$parent.$parent.submitAnswer(pce.getCode());
        });
      }]
    };
  }
]);

oppia.directive('oppiaResponsePencilCodeEditor', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'response/PencilCodeEditor',
      controller: ['$scope', '$attrs', function($scope, $attrs) {
        $scope.answer = oppiaHtmlEscaper.escapedJsonToObj($attrs.answer);
      }]
    };
  }
]);

oppia.directive('oppiaShortResponsePencilCodeEditor', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'shortResponse/PencilCodeEditor',
      controller: ['$scope', '$attrs', function($scope, $attrs) {
        $scope.answer = oppiaHtmlEscaper.escapedJsonToObj($attrs.answer);
      }]
    };
  }
]);

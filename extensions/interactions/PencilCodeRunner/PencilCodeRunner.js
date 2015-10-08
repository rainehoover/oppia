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
 * Directive for the PencilCodeRunner interaction.
 *
 * IMPORTANT NOTE: The naming convention for customization args that are passed
 * into the directive is: the name of the parameter, followed by 'With',
 * followed by the name of the arg.
 */
oppia.directive('oppiaInteractivePencilCodeRunner', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'interaction/PencilCodeRunner',
      controller: ['$scope', '$attrs', '$element',
          function($scope, $attrs, $element) {

        $scope.code = oppiaHtmlEscaper.escapedJsonToObj($attrs.codeWithValue);

        var pce = new PencilCodeEmbed($element[0].children[0]);
        pce.beginLoad($scope.code);
        pce.on('load', function() {
          // Hide the turtle.
          pce.setupScript([{
            code: 'ht();', type: 'text/coffeescript'
          }]);

          pce.hideToggleButton();
          pce.setReadOnly();
          pce.showEditor();
        });

        $scope.reset = function(newCode) {
          pce.setCode($scope.code);
        };

        pce.on('execute', function() {
          $scope.$parent.$parent.submitAnswer(null);
        });
      }]
    };
  }
]);

oppia.directive('oppiaResponsePencilCodeRunner', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'response/PencilCodeRunner'
    };
  }
]);

oppia.directive('oppiaShortResponsePencilCodeRunner', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'shortResponse/PencilCodeRunner'
    };
  }
]);

# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, softwar
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from extensions.interactions import base


class PencilCodeRunner(base.BaseInteraction):
    """Interaction for running code in Pencil Code."""

    name = 'Pencil Code Runner'
    description = 'Allows learners to run code in Pencil Code.'
    display_mode = base.DISPLAY_MODE_SUPPLEMENTAL
    is_trainable = False
    _dependency_ids = ['pencilcode']
    is_linear = True
    instructions = 'Click the \'Play\' button to run the code'
    needs_summary = False
    default_outcome_heading = 'When the \'Play\' button is clicked'

    _customization_arg_specs = [{
        'name': 'code',
        'description': 'The code to run',
        'schema': {
            'type': 'unicode',
            'ui_config': {
                'coding_mode': 'none',
            },
        },
        'default_value': '# Add code here for the learner to run.'
    }]

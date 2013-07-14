# coding: utf-8
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Models for Oppia widgets."""

__author__ = 'Sean Lip'

import copy
import os

from oppia.apps.base_model.models import BaseModel
from oppia.apps.classifier.models import Classifier
from oppia.apps.parameter.models import Parameter
from oppia.apps.parameter.models import ParameterProperty
import feconf
import utils

from google.appengine.ext import ndb
from google.appengine.ext.db import BadValueError
from google.appengine.ext.ndb import polymodel


class AnswerHandler(BaseModel):
    """An answer event stream (submit, click, drag, etc.)."""
    name = ndb.StringProperty(default='submit')
    # TODO(sll): Store a reference instead?
    classifier = ndb.StringProperty(choices=Classifier.get_classifier_ids())

    @property
    def rules(self):
        if not self.classifier:
            return []
        return Classifier.get(self.classifier).rules


class Widget(polymodel.PolyModel):
    """A superclass for NonInteractiveWidget and InteractiveWidget.

    NB: The ids for this class are strings that are the concatenations of:
      - the widget type (interactive|noninteractive)
      - a hyphen
      - the camel-cased version of the human-readable names.
    """
    @property
    def id(self):
        return self.key.id()

    # The human-readable name of the widget.
    name = ndb.StringProperty(required=True)
    # The category in the widget repository to which this widget belongs.
    category = ndb.StringProperty(required=True)
    # The description of the widget.
    description = ndb.TextProperty()
    # The widget static html template used for the response logging of
    # interactive widgets.
    static_template = ndb.TextProperty()
    # Parameter specifications for this widget. The default parameters can be
    # overridden when the widget is used within a State.
    params = ParameterProperty(repeated=True)

    @property
    def template(self):
        """The template used to generate the widget html."""
        widget_type, widget_id = self.id.split('-')
        return utils.get_file_contents(os.path.join(
            feconf.WIDGETS_DIR, widget_type, widget_id, '%s.html' % widget_id))

    @classmethod
    def get(cls, widget_id):
        """Gets a widget by id. If it does not exist, returns None."""
        # TODO(sll): Modify this to handle non-interactive widgets.
        return cls.get_by_id(widget_id)

    def put(self):
        """The put() method should only be called on subclasses of Widget."""
        if self.__class__.__name__ == 'Widget':
            raise NotImplementedError
        super(Widget, self).put()

    @classmethod
    def get_raw_code(cls, widget_id, params=None):
        """Gets the raw code for a parameterized widget."""
        if params is None:
            params = {}

        widget = cls.get(widget_id)

        # Parameters used to generate the raw code for the widget.
        # TODO(sll): Why do we convert only the default value to a JS string?
        parameters = dict(
            (param.name, params.get(
                param.name, utils.convert_to_js_string(param.value))
             ) for param in widget.params)

        return utils.parse_with_jinja(widget.template, parameters)

    @classmethod
    def _get_with_params(cls, widget_id, params):
        """Gets a dict representing a parameterized widget.

        This method must be called on a subclass of Widget.
        """
        if cls.__name__ == 'Widget':
            raise NotImplementedError

        widget = cls.get(widget_id)
        if widget is None:
            raise Exception('No widget found with id %s' % widget_id)

        result = copy.deepcopy(widget.to_dict(exclude=['class_']))
        result.update({
            'id': widget_id,
            'raw': cls.get_raw_code(widget_id, params),
            # TODO(sll): Restructure this so that it is
            # {key: {value: ..., obj_type: ...}}
            'params': dict((param.name, params.get(param.name, param.value))
                           for param in widget.params),
        })
        return result

    @classmethod
    def delete_all_widgets(cls):
        """Deletes all widgets."""
        widget_list = Widget.query()
        for widget in widget_list:
            widget.key.delete()


class NonInteractiveWidget(Widget):
    """A generic non-interactive widget."""

    @classmethod
    def load_default_widgets(cls):
        """Loads the default widgets."""
        widget_ids = os.listdir(feconf.NONINTERACTIVE_WIDGETS_DIR)

        for widget_id in widget_ids:
            widget_dir = os.path.join(
                feconf.NONINTERACTIVE_WIDGETS_DIR, widget_id)
            widget_conf_filename = '%s.config.yaml' % widget_id
            with open(os.path.join(widget_dir, widget_conf_filename)) as f:
                conf = utils.dict_from_yaml(f.read().decode('utf-8'))

            conf['id'] = '%s-%s' % (feconf.NONINTERACTIVE_PREFIX, widget_id)
            conf['params'] = [Parameter(**param) for param in conf['params']]
            # TODO(sll): Add a check that the template files exist.
            conf['static_template'] = ''

            widget = cls(**conf)
            widget.put()

    @classmethod
    def get_with_params(cls, widget_id, params):
        """Gets a dict representing a parameterized widget."""
        result = super(NonInteractiveWidget, cls)._get_with_params(
            widget_id, params)
        return result


class InteractiveWidget(Widget):
    """A generic interactive widget."""

    handlers = ndb.StructuredProperty(AnswerHandler, repeated=True)

    def _pre_put_hook(self):
        # Checks that at least one handler exists.
        if not self.handlers:
            raise BadValueError(
                'Widget %s has no handlers defined' % self.name)

        # Checks that all handler names are unique.
        names = [handler.name for handler in self.handlers]
        if len(set(names)) != len(names):
            raise BadValueError(
                'There are duplicate names in the handler for widget %s'
                % self.id)

    def _get_handler(self, handler_name):
        """Get the handler object corresponding to a given handler name."""
        return next((h for h in self.handlers if h.name == handler_name), None)

    @classmethod
    def load_default_widgets(cls):
        """Loads the default widgets.

        Assumes that everything is valid (directories exist, widget config files
        are formatted correctly, etc.).
        """
        widget_ids = os.listdir(feconf.INTERACTIVE_WIDGETS_DIR)

        for widget_id in widget_ids:
            widget_dir = os.path.join(feconf.INTERACTIVE_WIDGETS_DIR, widget_id)
            widget_conf_filename = '%s.config.yaml' % widget_id
            with open(os.path.join(widget_dir, widget_conf_filename)) as f:
                conf = utils.dict_from_yaml(f.read().decode('utf-8'))

            conf['id'] = '%s-%s' % (feconf.INTERACTIVE_PREFIX, widget_id)
            conf['params'] = [Parameter(**param) for param in conf['params']]
            conf['handlers'] = [AnswerHandler(**ah) for ah in conf['handlers']]
            # TODO(sll): Add a check that the template files exist.
            conf['static_template'] = ''
            static_path = os.path.join(widget_dir, '%s.static.html' % widget_id)
            if os.path.exists(static_path):
                conf['static_template'] = utils.get_file_contents(static_path)

            widget = cls(**conf)
            widget.put()

    def get_readable_name(self, handler_name, rule_rule):
        """Get the human-readable text for a rule."""
        handler = self._get_handler(handler_name)
        rule = next(r.name for r in handler.rules if r.rule == rule_rule)

        if rule:
            return rule
        raise Exception('No rule name found for %s' % rule_rule)

    @classmethod
    def get_with_params(cls, widget_id, params):
        """Gets a dict representing a parameterized widget."""
        result = super(InteractiveWidget, cls)._get_with_params(
            widget_id, params)

        widget = cls.get(widget_id)

        for idx, handler in enumerate(widget.handlers):
            result['handlers'][idx]['rules'] = dict(
                (rule.name, {'classifier': rule.rule, 'checks': rule.checks})
                for rule in handler.rules)

        return result

    @classmethod
    def get_raw_static_code(cls, widget_id, params=None):
        """Gets the static rendering raw code for a parameterized widget."""
        # TODO(kashida): Make this consistent with get_raw_code.
        if params is None:
            params = {}

        widget = cls.get(widget_id)
        return utils.parse_with_jinja(widget.static_template, params)
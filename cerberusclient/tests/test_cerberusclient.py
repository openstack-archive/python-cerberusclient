#
#   Copyright (c) 2015 EUROGICIEL
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

"""
test_python-cerberusclient
----------------------------------

Tests for `python-cerberusclient` module.
"""
import mock

from cerberusclient import client
from cerberusclient.tests import base
from cerberusclient.v1 import plugins
from cerberusclient.v1 import security_alarms
from cerberusclient.v1 import security_reports
from cerberusclient.v1 import tasks


def my_mock(*a, **b):
    return [a, b]


def my_mock_plugin(*a, **b):
    b['plugin'] = b
    return [a, b]


def my_mock_task(*a, **b):
    b['task'] = b
    return [a, b]


def my_mock_security_report(*a, **b):
    b['security_report'] = b
    return [a, b]


def my_mock_security_alarm(*a, **b):
    b['security_alarm'] = b
    return [a, b]

api = mock.MagicMock(json_request=my_mock)


class TestCerberusclient(base.TestCase):

    def test_create_client_instance(self):
        endpoint = 'http://no-resolved-host:8001'
        test_client = client.Client('1', endpoint=endpoint,
                                    token='1', timeout=10)
        self.assertIsNotNone(test_client.plugins)

    def test_plugin_manager_list(self):
        manager = plugins.PluginManager(api)
        result = manager.list()
        self.assertEqual([], result)

    def test_plugin_manager_get(self):
        api = mock.MagicMock(json_request=my_mock_plugin)
        manager = plugins.PluginManager(api)
        result = manager.get('test')
        self.assertIsNotNone(result.manager)

    def test_task_manager_create(self):
        api = mock.MagicMock(json_request=my_mock_task)
        manager = tasks.TaskManager(api)
        result = manager.create('test', 'method')
        self.assertIsNotNone(result.manager)

    def test_task_manager_list(self):
        manager = tasks.TaskManager(api)
        result = manager.list()
        self.assertEqual([], result)

    def test_task_manager_get(self):
        api = mock.MagicMock(json_request=my_mock_task)
        manager = tasks.TaskManager(api)
        result = manager.get('test')
        self.assertIsNotNone(result.manager)

    def test_task_manager_stop(self):
        api = mock.MagicMock()
        manager = tasks.TaskManager(api)
        result = manager.stop(1)
        self.assertIsNone(result)

    def test_task_manager_delete(self):
        api = mock.MagicMock()
        manager = tasks.TaskManager(api)
        result = manager.delete(1)
        self.assertIsNone(result)

    def test_task_manager_force_delete(self):
        api = mock.MagicMock()
        manager = tasks.TaskManager(api)
        result = manager.force_delete(1)
        self.assertIsNone(result)

    def test_task_manager_restart(self):
        api = mock.MagicMock()
        manager = tasks.TaskManager(api)
        result = manager.restart(1)
        self.assertIsNone(result)

    def test_security_reports_manager_list(self):
        manager = security_reports.SecurityReportManager(api)
        result = manager.list()
        self.assertIsNotNone(result)

    def test_security_reports_manager_get(self):
        api = mock.MagicMock(json_request=my_mock_security_report)
        manager = security_reports.SecurityReportManager(api)
        result = manager.get('report_id')
        self.assertIsNotNone(result)

    def test_security_alarms_manager_list(self):
        manager = security_alarms.SecurityAlarmManager(api)
        result = manager.list()
        self.assertIsNotNone(result)

    def test_security_alarms_manager_get(self):
        api = mock.MagicMock(json_request=my_mock_security_alarm)
        manager = security_alarms.SecurityAlarmManager(api)
        result = manager.get('alarm_id')
        self.assertIsNotNone(result)

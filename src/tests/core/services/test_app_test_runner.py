import logging

import pytest

from core.services.runners import AppTestRunner
from tests.mocks.mock_subprocess import logger, mock_popen


@mock_popen("core.services.runners.test.subprocess")
def test_app_test_runner_e2e_tests(caplog):
    caplog.set_level(logging.INFO)

    test_runner = AppTestRunner(p_logger=logger)
    test_runner(e2e=True)

    assert "Preparing to run e2e tests." in caplog.text
    assert "Start running tests." in caplog.text
    assert "Process executed successfully." in caplog.text


@mock_popen("core.services.runners.test.subprocess")
def test_app_test_runner_target_apps(caplog):
    caplog.set_level(logging.INFO)
    test_runner = AppTestRunner(p_logger=logger)

    test_runner(target_apps=["user"])
    assert "Preparing to run e2e tests." not in caplog.text
    assert "Start running tests." in caplog.text
    assert "Process executed successfully." in caplog.text


@mock_popen("core.services.runners.test.subprocess")
def test_app_test_runner_invalid_inputs(caplog):
    caplog.set_level(logging.INFO)

    test_runner = AppTestRunner(p_logger=logger)
    with pytest.raises(ValueError) as e:
        test_runner(test_paths=["user/tests/test_user.py"], target_apps=["user"])
    assert "Cannot specify both 'target_app' and 'test_paths'." in str(e.value)


@mock_popen("core.services.runners.test.subprocess", error=1)
def test_app_test_runner_migrations_already_executed(caplog):
    caplog.set_level(logging.INFO)
    test_runner = AppTestRunner(p_logger=logger)
    test_runner(e2e=True)
    assert "ERROR" in caplog.text
    assert "Migrations already applied." in caplog.text

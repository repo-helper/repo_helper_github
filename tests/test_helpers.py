# stdlib
import re

# 3rd party
import click
import pytest
from consolekit.testing import CliRunner, Result
from domdf_python_tools.testing import check_file_regression

# this package
from repo_helper_github import __version__, echo_rate_limit, get_user
from repo_helper_github.cli import github


def test_rate_limit(github_manager, capsys, file_regression, cassette):
	with echo_rate_limit(github_manager.github):
		pass

	check_file_regression(capsys.readouterr().out, file_regression)


def test_assert_org_member(github_manager, file_regression, capsys, cassette):
	with pytest.raises(click.Abort):
		github_manager.assert_org_member(get_user(github_manager.github))

	check_file_regression(capsys.readouterr().err, file_regression, extension=".md")


def test_version(tmp_pathplus):
	runner = CliRunner()

	result: Result = runner.invoke(github, args=["--version"])
	assert result.exit_code == 0
	assert re.match(f"repo_helper_github version {__version__}", result.stdout.rstrip())

	result = runner.invoke(github, args=["--version", "--version"])
	assert result.exit_code == 0
	assert re.match(f"repo_helper_github version {__version__}, repo_helper .*", result.stdout.rstrip())

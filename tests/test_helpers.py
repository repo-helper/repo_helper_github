# stdlib
import re

# 3rd party
import click
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus
from github3_utils import echo_rate_limit, get_user

# this package
from repo_helper_github import __version__
from repo_helper_github.cli import github


def test_rate_limit(
		github_manager,
		capsys,
		advanced_file_regression: AdvancedFileRegressionFixture,
		cassette,
		):
	with echo_rate_limit(github_manager.github):
		pass

	advanced_file_regression.check(capsys.readouterr().out)


def test_assert_org_member(
		github_manager,
		advanced_file_regression: AdvancedFileRegressionFixture,
		capsys,
		cassette,
		):
	with pytest.raises(click.Abort):
		github_manager.assert_org_member(get_user(github_manager.github))

	advanced_file_regression.check(capsys.readouterr().err, extension=".md")


def test_version(tmp_pathplus: PathPlus):
	runner = CliRunner()

	result: Result = runner.invoke(github, args=["--version"])
	assert result.exit_code == 0
	assert re.match(f"repo_helper_github version {__version__}", result.stdout.rstrip())

	result = runner.invoke(github, args=["--version", "--version"])
	assert result.exit_code == 0
	assert re.match(f"repo_helper_github version {__version__}, repo_helper .*", result.stdout.rstrip())

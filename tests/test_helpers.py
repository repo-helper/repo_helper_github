# stdlib
import re

# 3rd party
import click
import pytest
from betamax import Betamax  # type: ignore
from click.testing import CliRunner, Result
from domdf_python_tools.testing import check_file_regression

# this package
from repo_helper_github import __version__, echo_rate_limit
from repo_helper_github.cli import github


def test_rate_limit(github_manager, capsys, file_regression):
	with Betamax(github_manager.github.session) as vcr:
		vcr.use_cassette("rate_limit", record="once")

		with echo_rate_limit(github_manager.github):
			pass

		check_file_regression(capsys.readouterr().out, file_regression)


def test_assert_org_member(github_manager, file_regression, capsys):
	with Betamax(github_manager.github.session) as vcr:
		vcr.use_cassette("assert_org_member", record="once")

		with pytest.raises(click.Abort):
			github_manager.assert_org_member(github_manager.github.get_user())

		check_file_regression(capsys.readouterr().err, file_regression, extension=".md")


def test_version(tmp_pathplus):
	runner = CliRunner()

	result: Result = runner.invoke(github, catch_exceptions=False, args=["--version"])
	assert result.exit_code == 0
	assert re.match(f"repo_helper_github version {__version__}", result.stdout.rstrip())

	result = runner.invoke(github, catch_exceptions=False, args=["--version", "--version"])
	assert result.exit_code == 0
	assert re.match(f"repo_helper_github version {__version__}, repo_helper .*", result.stdout.rstrip())

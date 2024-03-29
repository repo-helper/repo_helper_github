# stdlib
import re

# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from github3_utils import echo_rate_limit, get_user

# this package
from repo_helper_github import GitHubManager, OrganizationError, __version__
from repo_helper_github.cli import github


@pytest.mark.usefixtures("cassette")
def test_rate_limit(
		github_manager: GitHubManager,
		capsys,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	with echo_rate_limit(github_manager.github):
		pass

	advanced_file_regression.check(capsys.readouterr().out)


@pytest.mark.usefixtures("cassette")
def test_assert_org_member(
		github_manager: GitHubManager,
		capsys,
		):

	error_msg = (
			r"Either the organization configured in 'repo_helper.yml' \(domdfcoding\) does not exist "
			r"or the authenticated user \(domdfcoding\) is not a member!"
			)

	with pytest.raises(OrganizationError, match=error_msg):
		github_manager.assert_org_member(get_user(github_manager.github))

	capout = capsys.readouterr()
	assert not capout.out
	assert not capout.err


def test_version():
	runner = CliRunner()

	result: Result = runner.invoke(github, args=["--version"])
	assert result.exit_code == 0
	assert re.match(f"repo_helper_github version {__version__}", result.stdout.rstrip())

	result = runner.invoke(github, args=["--version", "--version"])
	assert result.exit_code == 0
	assert re.match(f"repo_helper_github version {__version__}, repo_helper .*", result.stdout.rstrip())

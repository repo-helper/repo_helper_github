# 3rd party
import pytest
from betamax import Betamax  # type: ignore
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from domdf_python_tools.testing import check_file_regression
from github3.exceptions import UnprocessableEntity  # type: ignore

# this package
from repo_helper_github.cli import new


def test_create_repo(github_manager, temp_empty_repo, example_config):
	with Betamax(github_manager.github.session) as vcr:
		vcr.use_cassette("creation", record="once")

		github_manager.new()

		github_manager.github.repository("domdfcoding", "repo_helper_demo")

		with pytest.raises(UnprocessableEntity, match="422 Repository creation failed."):
			github_manager.new()


def test_via_cli(betamax_github_session, temp_github_repo, file_regression, github_manager):
	with Betamax(betamax_github_session) as vcr:
		vcr.use_cassette("creation", record="once")

		with in_directory(temp_github_repo):
			runner = CliRunner()
			result: Result = runner.invoke(new, catch_exceptions=False)

		assert result.exit_code == 0
		check_file_regression(result.stdout.rstrip(), file_regression, extension=".md")

		# Check the repository now exists
		github_manager.github.repository("domdfcoding", "repo_helper_demo")

		with pytest.raises(UnprocessableEntity, match="422 Repository creation failed."):
			github_manager.new()

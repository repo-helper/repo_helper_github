# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from github3.exceptions import UnprocessableEntity

# this package
from repo_helper_github.cli import new


def test_create_repo(github_manager, temp_github_repo, module_cassette):
	with in_directory(temp_github_repo):
		github_manager.new()

		github_manager.github.repository("domdfcoding", "repo_helper_demo")

		with pytest.raises(UnprocessableEntity, match="422 Repository creation failed."):
			github_manager.new()


def test_via_cli(
		betamax_github_session,
		temp_github_repo,
		advanced_file_regression: AdvancedFileRegressionFixture,
		github_manager,
		module_cassette,
		):
	with in_directory(temp_github_repo):
		runner = CliRunner()
		result: Result = runner.invoke(new)

	assert result.exit_code == 0
	result.check_stdout(advanced_file_regression, extension=".md")

	# Check the repository now exists
	github_manager.github.repository("domdfcoding", "repo_helper_demo")

	with pytest.raises(UnprocessableEntity, match="422 Repository creation failed."):
		github_manager.new()

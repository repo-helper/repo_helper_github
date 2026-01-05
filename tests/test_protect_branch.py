# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from repo_helper_github import GitHubManager, compile_required_checks
from repo_helper_github.cli import protect_branch


@pytest.mark.usefixtures("module_cassette")
def test_protect_branch(github_manager: GitHubManager):
	github_manager.protect_branch("master")

	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
	branch = repo.branch("master")

	assert branch.protection().required_status_checks.contexts() == list(compile_required_checks(github_manager))


@pytest.mark.usefixtures("betamax_github_session", "module_cassette")
def test_via_cli(
		temp_github_repo: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		github_manager: GitHubManager,
		):
	with in_directory(temp_github_repo):
		runner = CliRunner()
		result: Result = runner.invoke(protect_branch, args=["master"])

	result.check_stdout(advanced_file_regression, extension=".md")
	assert result.exit_code == 0

	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
	branch = repo.branch("master")

	assert branch.protection().required_status_checks.contexts() == list(compile_required_checks(github_manager))

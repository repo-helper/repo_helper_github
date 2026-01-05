# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from repo_helper_github import GitHubManager
from repo_helper_github.cli import update


@pytest.mark.usefixtures("cassette")
def test_update_topics(github_manager: GitHubManager):
	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
	github_manager.update_topics(repo)

	assert set(repo.topics().names) == {"python", "repo-helper", "github", "configuration"}


@pytest.mark.usefixtures("module_cassette")
def test_update(github_manager: GitHubManager, temp_github_repo: PathPlus):
	with in_directory(temp_github_repo):
		github_manager.update()

	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")

	assert set(repo.topics().names) == {"python", "repo-helper", "github", "configuration"}
	assert repo.description == "Update multiple configuration files, build scripts etc. from a single location."


@pytest.mark.usefixtures("betamax_github_session", "module_cassette")
def test_via_cli(
		temp_github_repo: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		github_manager: GitHubManager,
		):
	with in_directory(temp_github_repo):
		runner = CliRunner()
		result: Result = runner.invoke(update)

	result.check_stdout(advanced_file_regression, extension=".md")
	assert result.exit_code == 0

	# Check the repository has been updated
	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")

	assert set(repo.topics().names) == {"python", "repo-helper", "github", "configuration"}
	assert repo.description == "Update multiple configuration files, build scripts etc. from a single location."

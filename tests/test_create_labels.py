# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory
from github3_utils.check_labels import check_status_labels

# this package
from repo_helper_github import GitHubManager
from repo_helper_github.cli import labels


@pytest.mark.usefixtures("module_cassette")
def test_create_labels(github_manager: GitHubManager):
	assert github_manager.create_labels() == 0

	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
	current_labels = {label.name: label for label in repo.labels()}

	for label in check_status_labels:
		assert label in current_labels


@pytest.mark.usefixtures("betamax_github_session", "module_cassette")
def test_via_cli(
		temp_github_repo: PathPlus,
		advanced_file_regression: AdvancedFileRegressionFixture,
		github_manager: GitHubManager,
		):

	with in_directory(temp_github_repo):
		runner = CliRunner()
		result: Result = runner.invoke(labels)

	assert result.exit_code == 0
	result.check_stdout(advanced_file_regression, extension=".md")

	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
	current_labels = {label.name: label for label in repo.labels()}

	for label in check_status_labels:
		assert label in current_labels

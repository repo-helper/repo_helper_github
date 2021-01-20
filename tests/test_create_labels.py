# 3rd party
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from domdf_python_tools.testing import check_file_regression
from github3_utils.check_labels import check_status_labels

# this package
from repo_helper_github.cli import labels


def test_create_labels(github_manager, module_cassette):
	assert github_manager.create_labels() == 0

	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
	current_labels = {label.name: label for label in repo.labels()}

	for label in check_status_labels:
		assert label in current_labels


def test_via_cli(betamax_github_session, temp_github_repo, file_regression, github_manager, module_cassette):
	with in_directory(temp_github_repo):
		runner = CliRunner()
		result: Result = runner.invoke(labels, catch_exceptions=False)

	assert result.exit_code == 0
	check_file_regression(result.stdout.rstrip(), file_regression, extension=".md")

	repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
	current_labels = {label.name: label for label in repo.labels()}

	for label in check_status_labels:
		assert label in current_labels

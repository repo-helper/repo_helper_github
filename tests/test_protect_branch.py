# 3rd party
from betamax import Betamax  # type: ignore
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from domdf_python_tools.testing import check_file_regression

# this package
from repo_helper_github import compile_required_checks
from repo_helper_github.cli import protect_branch


def test_protect_branch(github_manager):
	with Betamax(github_manager.github.session) as vcr:
		vcr.use_cassette("protect_branch", record="once")

		github_manager.protect_branch("master")

		repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
		branch = repo.branch("master")

		assert branch.protection().required_status_checks.contexts() == list(
				compile_required_checks(github_manager)
				)


def test_via_cli(betamax_github_session, temp_github_repo, file_regression, github_manager):
	with Betamax(betamax_github_session) as vcr:
		vcr.use_cassette("protect_branch", record="once")

		with in_directory(temp_github_repo):
			runner = CliRunner()
			result: Result = runner.invoke(protect_branch, catch_exceptions=False, args=["master"])

		assert result.exit_code == 0
		check_file_regression(result.stdout.rstrip(), file_regression, extension=".md")

		repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
		branch = repo.branch("master")

		assert branch.protection().required_status_checks.contexts() == list(
				compile_required_checks(github_manager)
				)

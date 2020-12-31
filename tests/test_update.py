# 3rd party
from betamax import Betamax  # type: ignore
from click.testing import CliRunner, Result
from domdf_python_tools.paths import in_directory
from domdf_python_tools.testing import check_file_regression

# this package
from repo_helper_github.cli import update


def test_update_topics(github_manager):
	with Betamax(github_manager.github.session) as vcr:
		vcr.use_cassette("update_topics", record="once")

		repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")
		github_manager.update_topics(repo)

		assert set(repo.topics().names) == {"python", "repo-helper", "github", "configuration"}


def test_update(github_manager):
	with Betamax(github_manager.github.session) as vcr:
		vcr.use_cassette("update", record="once")

		github_manager.update()

		repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")

		assert set(repo.topics().names) == {"python", "repo-helper", "github", "configuration"}
		assert repo.description == "Update multiple configuration files, build scripts etc. from a single location."


def test_via_cli(betamax_github_session, temp_github_repo, file_regression, github_manager):

	with Betamax(betamax_github_session) as vcr:
		vcr.use_cassette("update", record="once")

		with in_directory(temp_github_repo):
			runner = CliRunner()
			result: Result = runner.invoke(update, catch_exceptions=False)

		assert result.exit_code == 0
		check_file_regression(result.stdout.rstrip(), file_regression, extension=".md")

		# Check the repository has been updated
		repo = github_manager.github.repository("domdfcoding", "repo_helper_demo")

		assert set(repo.topics().names) == {"python", "repo-helper", "github", "configuration"}
		assert repo.description == "Update multiple configuration files, build scripts etc. from a single location."

# 3rd party
import pytest
from _pytest.fixtures import FixtureRequest
from betamax import Betamax  # type: ignore
from domdf_python_tools.paths import PathPlus
from github3.session import GitHubSession  # type: ignore

# this package
from repo_helper_github import GitHubManager
from repo_helper_github._github import Github

with Betamax.configure() as config:
	config.cassette_library_dir = PathPlus(__file__).parent / "cassettes"

pytest_plugins = ("domdf_python_tools.testing", "repo_helper.testing")


@pytest.fixture()
def temp_github_repo(temp_empty_repo, tmp_pathplus, example_config) -> PathPlus:
	(tmp_pathplus / "repo_helper.yml").write_lines([
			*example_config.splitlines()[:8],
			*example_config.splitlines()[10:],
			'',
			"keywords:",
			"   - repo_helper",
			"   - github",
			"   - configuration",
			'',
			])

	return tmp_pathplus


@pytest.fixture()
def github_manager(temp_github_repo):
	return GitHubManager(
			"FAKE_TOKEN",
			temp_github_repo,
			verbose=True,
			colour=False,
			)


@pytest.fixture()
def betamax_github_session(monkeypatch):
	monkeypatch.setenv("GITHUB_TOKEN", "FAKE_TOKEN")

	session = GitHubSession()

	def __init__(self, username='', password='', token='', *args, **kwargs):
		super(Github, self).__init__(username=username, password=password, token=token, session=session)

	monkeypatch.setattr(Github, "__init__", __init__)

	return session


@pytest.fixture()
def cassette(request: FixtureRequest, github_manager):
	cassette_name = request.node.name

	with Betamax(github_manager.github.session) as vcr:
		vcr.use_cassette(cassette_name, record="none")
		# print(f"Using cassette {cassette_name!r}")

		yield github_manager


@pytest.fixture()
def module_cassette(request: FixtureRequest, github_manager):
	cassette_name = request.module.__name__

	with Betamax(github_manager.github.session) as vcr:
		vcr.use_cassette(cassette_name, record="none")
		# print(f"Using cassette {cassette_name!r}")

		yield github_manager
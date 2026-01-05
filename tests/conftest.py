# 3rd party
import pytest
from betamax import Betamax  # type: ignore[import-untyped]
from domdf_python_tools.paths import PathPlus
from github3 import GitHub
from github3.session import GitHubSession

# this package
from repo_helper_github import GitHubManager
from repo_helper_github._github import Github

with Betamax.configure() as config:
	config.cassette_library_dir = PathPlus(__file__).parent / "cassettes"

pytest_plugins = ("coincidence", "github3_utils.testing", "repo_helper.testing")


@pytest.fixture()
def temp_github_repo(temp_empty_repo: PathPlus, example_config: str) -> PathPlus:
	(temp_empty_repo / "repo_helper.yml").write_lines([
			*example_config.splitlines()[:8],
			*example_config.splitlines()[10:],
			'',
			"keywords:",
			"   - repo_helper",
			"   - github",
			"   - configuration",
			'',
			])

	return temp_empty_repo


@pytest.fixture()
def github_manager(temp_github_repo: PathPlus) -> GitHubManager:
	return GitHubManager(
			"FAKE_TOKEN",
			temp_github_repo,
			verbose=True,
			colour=False,
			)


@pytest.fixture()
def betamax_github_session(monkeypatch) -> GitHubSession:
	monkeypatch.setenv("GITHUB_TOKEN", "FAKE_TOKEN")

	session = GitHubSession()

	def __init__(self, username: str = '', password: str = '', token: str = '', *args, **kwargs):
		super(Github, self).__init__(username=username, password=password, token=token, session=session)

	monkeypatch.setattr(Github, "__init__", __init__)

	return session


@pytest.fixture()
def github_client(github_manager: GitHubManager) -> GitHub:
	return github_manager.github

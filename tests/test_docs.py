import difflib
from pathlib import Path

readme_path = Path(__file__).parent.parent / "README.md"


def test_readme_contains_latest_help(cli_runner):
    result = cli_runner(["--help"], terminal_width=88)
    help_text = result.output
    # This should be in the README
    help_text = help_text.replace("Usage: cli ", "Usage: db-to-sqlite ")
    readme = readme_path.read_text()
    assert help_text in readme

from pathlib import Path

from click.testing import CliRunner

from db_to_sqlite.cli import cli

readme_path = Path(__file__).parent.parent / "README.md"


def test_readme_contains_latest_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"], terminal_width=88)
    help_text = result.output
    # The 4-space indented version of this should be in README.md
    help_text_indented = "\n".join(
        [
            ("    {}".format(line) if line.strip() else "")
            for line in help_text.split("\n")
        ]
    ).replace("Usage: cli ", "Usage: db-to-sqlite ")
    readme = readme_path.read_text()
    assert help_text_indented in readme

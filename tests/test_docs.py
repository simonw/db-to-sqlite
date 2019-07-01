import difflib
from pathlib import Path

readme_path = Path(__file__).parent.parent / "README.md"


def test_readme_contains_latest_help(cli_runner):
    result = cli_runner(["--help"], terminal_width=88)
    help_text = result.output
    # The 4-space indented version of this should be in README.md
    help_text_indented = "\n".join(
        [
            ("    {}".format(line) if line.strip() else "")
            for line in help_text.splitlines()
        ]
    ).replace("Usage: cli ", "Usage: db-to-sqlite ")
    readme = readme_path.read_text()
    # Compare to just lines starting with 'Usage: db-to-sqlite' and ending --help
    relevant_lines = []
    collecting = False
    for line in readme.splitlines():
        if collecting:
            relevant_lines.append(line)
            if line.strip().startswith("--help"):
                break
        elif line.strip().startswith("Usage: db-to-sqlite"):
            relevant_lines.append(line)
            collecting = True
    relevant_text = "\n".join(relevant_lines)
    if help_text_indented != relevant_text:
        print(
            "\n".join(
                difflib.ndiff(
                    relevant_text.splitlines(), help_text_indented.splitlines()
                )
            )
        )
        assert False

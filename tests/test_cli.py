"""Tests for CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from archsight.cli import app

runner = CliRunner()


class TestScanCommand:
    def test_scan_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "scan" in result.stdout

    def test_scan_python_complex(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex"
        result = runner.invoke(app, ["scan", str(project)])
        assert result.exit_code == 0
        assert "python" in result.stdout

    def test_scan_python_cyclic(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex_cyclic"
        result = runner.invoke(app, ["scan", str(project)])
        assert result.exit_code == 0
        assert "Cycles" in result.stdout

    def test_scan_fail_on_cycle_exits_one(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex_cyclic"
        result = runner.invoke(app, ["scan", str(project), "--fail-on-cycle"])
        assert result.exit_code == 1

    def test_scan_fail_on_cycle_exits_zero_when_no_cycles(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex"
        result = runner.invoke(app, ["scan", str(project), "--fail-on-cycle"])
        assert result.exit_code == 0

    def test_scan_json_output(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex"
        result = runner.invoke(app, ["scan", str(project), "--format", "json"])
        assert result.exit_code == 0
        assert "project_path" in result.stdout

    def test_scan_markdown_output(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex"
        result = runner.invoke(app, ["scan", str(project), "--format", "markdown"])
        assert result.exit_code == 0
        assert "archsight Analysis Report" in result.stdout

    def test_scan_only_flag(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex_cyclic"
        result = runner.invoke(app, ["scan", str(project), "--only", "cycles"])
        assert result.exit_code == 0
        assert "Cycles" in result.stdout

    def test_scan_output_to_file(self, tmp_path: Path) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex"
        output = tmp_path / "report.json"
        result = runner.invoke(app, ["scan", str(project), "--format", "json", "-o", str(output)])
        assert result.exit_code == 0
        assert output.exists()


class TestImpactCommand:
    def test_impact_help(self) -> None:
        result = runner.invoke(app, ["impact", "--help"])
        assert result.exit_code == 0

    def test_impact_on_file(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex"
        result = runner.invoke(app, ["impact", str(project), "main.py"])
        assert result.exit_code == 0
        assert "Impact Analysis" in result.stdout

    def test_impact_on_missing_file(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex"
        result = runner.invoke(app, ["impact", str(project), "nonexistent.py"])
        assert result.exit_code == 1


class TestTemporalCommand:
    def test_temporal_help(self) -> None:
        result = runner.invoke(app, ["temporal", "--help"])
        assert result.exit_code == 0

    def test_temporal_without_gitpython(self) -> None:
        project = Path(__file__).parent / "fixtures" / "python_complex"
        result = runner.invoke(app, ["temporal", str(project)])
        assert result.exit_code == 1

"""Basic CLI tests."""

from typer.testing import CliRunner

from dom.cli import app

runner = CliRunner()


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "dom version" in result.stdout


def test_help():
    """Test help is shown."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "DigitalOcean Infrastructure Manager" in result.stdout


def test_audit_help():
    """Test audit subcommand help."""
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "Audit" in result.stdout


def test_costs_help():
    """Test costs subcommand help."""
    result = runner.invoke(app, ["costs", "--help"])
    assert result.exit_code == 0


def test_cleanup_help():
    """Test cleanup subcommand help."""
    result = runner.invoke(app, ["cleanup", "--help"])
    assert result.exit_code == 0


def test_export_help():
    """Test export subcommand help."""
    result = runner.invoke(app, ["export", "--help"])
    assert result.exit_code == 0

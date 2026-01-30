"""Terraform wrapper commands."""

import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(no_args_is_help=True)
console = Console()

TERRAFORM_DIR = Path("./terraform")
GENERATED_DIR = TERRAFORM_DIR / "generated"


def run_terraform(args: list[str], cwd: Path = TERRAFORM_DIR) -> int:
    """Run terraform command."""
    cmd = ["terraform"] + args
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]\n")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


@app.command("init")
def tf_init():
    """Initialize Terraform (terraform init)."""
    run_terraform(["init"])


@app.command("plan")
def tf_plan():
    """Show planned changes (terraform plan)."""
    run_terraform(["plan"])


@app.command("apply")
def tf_apply(
    auto_approve: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Apply changes (terraform apply)."""
    args = ["apply"]
    if auto_approve:
        args.append("-auto-approve")
    run_terraform(args)


@app.command("destroy")
def tf_destroy(
    auto_approve: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Destroy infrastructure (terraform destroy)."""
    args = ["destroy"]
    if auto_approve:
        args.append("-auto-approve")
    run_terraform(args)


@app.command("import")
def tf_import():
    """Run import.sh to import existing resources."""
    import_script = GENERATED_DIR / "import.sh"

    if not import_script.exists():
        console.print(f"[red]Error:[/red] {import_script} not found")
        console.print("Run 'dom export terraform' first")
        raise typer.Exit(1)

    console.print(f"[bold]Running {import_script}[/bold]\n")

    # Read and execute each line
    with open(import_script) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                console.print(f"[dim]$ {line}[/dim]")
                result = subprocess.run(line, shell=True, cwd=TERRAFORM_DIR)
                if result.returncode != 0:
                    console.print(f"[yellow]Warning: command failed[/yellow]")


@app.command("output")
def tf_output():
    """Show Terraform outputs."""
    run_terraform(["output"])


@app.command("state")
def tf_state():
    """List resources in Terraform state."""
    run_terraform(["state", "list"])


@app.command("fmt")
def tf_fmt():
    """Format Terraform files."""
    run_terraform(["fmt", "-recursive"])


@app.command("validate")
def tf_validate():
    """Validate Terraform configuration."""
    run_terraform(["validate"])

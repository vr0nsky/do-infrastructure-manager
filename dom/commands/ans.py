"""Ansible wrapper commands."""

import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(no_args_is_help=True)
console = Console()

ANSIBLE_DIR = Path("./ansible")
INVENTORY_DIR = Path("./inventory")  # Relative to ANSIBLE_DIR
PLAYBOOKS_DIR = Path("./playbooks")  # Relative to ANSIBLE_DIR


def get_inventory_file() -> Path:
    """Get the inventory file path (relative to ANSIBLE_DIR)."""
    ini_file = ANSIBLE_DIR / "inventory" / "inventory.ini"
    yml_file = ANSIBLE_DIR / "inventory" / "inventory.yml"

    if ini_file.exists():
        return INVENTORY_DIR / "inventory.ini"
    elif yml_file.exists():
        return INVENTORY_DIR / "inventory.yml"
    else:
        console.print(f"[red]Error:[/red] No inventory found in {ANSIBLE_DIR / 'inventory'}")
        console.print("Run 'dom export ansible' first")
        raise typer.Exit(1)


def run_ansible(args: list[str]) -> int:
    """Run ansible command."""
    cmd = ["ansible"] + args
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]\n")
    result = subprocess.run(cmd, cwd=ANSIBLE_DIR)
    return result.returncode


def run_ansible_playbook(args: list[str]) -> int:
    """Run ansible-playbook command."""
    cmd = ["ansible-playbook"] + args
    console.print(f"[dim]$ {' '.join(cmd)}[/dim]\n")
    result = subprocess.run(cmd, cwd=ANSIBLE_DIR)
    return result.returncode


@app.command("ping")
def ans_ping(
    host: str = typer.Argument("all", help="Host pattern (default: all)"),
):
    """Ping hosts to test connectivity."""
    inventory = get_inventory_file()
    run_ansible(["-i", str(inventory), host, "-m", "ping"])


@app.command("play")
def ans_play(
    playbook: str = typer.Argument(..., help="Playbook name (e.g., setup-base.yml)"),
    host: str = typer.Option("all", "--limit", "-l", help="Limit to specific hosts"),
    check: bool = typer.Option(False, "--check", "-C", help="Dry run mode"),
):
    """Run an Ansible playbook."""
    inventory = get_inventory_file()
    full_playbooks_dir = ANSIBLE_DIR / "playbooks"

    # Find playbook
    playbook_path = full_playbooks_dir / playbook
    if not playbook_path.exists():
        # Try without .yml extension
        playbook_path = full_playbooks_dir / f"{playbook}.yml"

    if not playbook_path.exists():
        console.print(f"[red]Error:[/red] Playbook not found: {playbook}")
        console.print(f"\nAvailable playbooks in {full_playbooks_dir}:")
        for p in full_playbooks_dir.glob("*.yml"):
            console.print(f"  - {p.name}")
        raise typer.Exit(1)

    args = ["-i", str(inventory), str(PLAYBOOKS_DIR / playbook_path.name)]
    if host != "all":
        args.extend(["--limit", host])
    if check:
        args.append("--check")

    run_ansible_playbook(args)


@app.command("inventory")
def ans_inventory():
    """Show current inventory."""
    inventory = get_inventory_file()
    full_path = ANSIBLE_DIR / inventory

    console.print(f"\n[bold]Inventory:[/bold] {full_path}\n")

    with open(full_path) as f:
        content = f.read()

    console.print(content)


@app.command("list")
def ans_list():
    """List all hosts in inventory."""
    inventory = get_inventory_file()
    run_ansible(["-i", str(inventory), "all", "--list-hosts"])


@app.command("facts")
def ans_facts(
    host: str = typer.Argument(..., help="Host to gather facts from"),
):
    """Gather facts from a host."""
    inventory = get_inventory_file()
    run_ansible(["-i", str(inventory), host, "-m", "setup"])


@app.command("shell")
def ans_shell(
    command: str = typer.Argument(..., help="Command to run"),
    host: str = typer.Option("all", "--host", "-h", help="Host pattern"),
):
    """Run a shell command on hosts."""
    inventory = get_inventory_file()
    run_ansible(["-i", str(inventory), host, "-m", "shell", "-a", command])


@app.command("playbooks")
def ans_playbooks():
    """List available playbooks."""
    full_playbooks_dir = ANSIBLE_DIR / "playbooks"
    console.print(f"\n[bold]Available Playbooks:[/bold] {full_playbooks_dir}\n")

    playbooks = list(full_playbooks_dir.glob("*.yml"))

    if not playbooks:
        console.print("[dim]No playbooks found[/dim]")
        return

    table = Table()
    table.add_column("Playbook", style="green")
    table.add_column("Description")

    for p in playbooks:
        # Try to extract description from first comment or name
        desc = "-"
        with open(p) as f:
            first_line = f.readline().strip()
            if first_line.startswith("#"):
                desc = first_line[1:].strip()
        table.add_row(p.name, desc)

    console.print(table)

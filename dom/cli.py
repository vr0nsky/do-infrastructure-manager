"""Main CLI entry point."""

import typer
from rich.console import Console

from dom.commands import audit, costs, cleanup, export

app = typer.Typer(
    name="dom",
    help="DigitalOcean Infrastructure Manager - Audit, manage and export your DO resources.",
    no_args_is_help=True,
)

console = Console()

# Register sub-commands
app.add_typer(audit.app, name="audit", help="Audit and list DigitalOcean resources")
app.add_typer(costs.app, name="costs", help="Analyze costs and billing")
app.add_typer(cleanup.app, name="cleanup", help="Find orphaned or unused resources")
app.add_typer(export.app, name="export", help="Export resources to Terraform/Ansible")


@app.command()
def version():
    """Show version information."""
    from dom import __version__
    console.print(f"dom version {__version__}")


@app.command()
def tui():
    """Launch interactive TUI (Terminal User Interface)."""
    import os
    from dom.tui import DOManagerApp
    app = DOManagerApp()
    result = app.run()
    if result and result.startswith("ssh "):
        os.system(result)


@app.command()
def status():
    """Quick status check of your DigitalOcean account."""
    from dom.utils import get_client

    client = get_client()

    console.print("\n[bold]DigitalOcean Account Status[/bold]\n")

    # Account info
    account = client.account.get()["account"]
    console.print(f"  Email: {account['email']}")
    console.print(f"  Status: {account['status']}")
    console.print(f"  Droplet Limit: {account['droplet_limit']}")

    # Quick resource count
    droplets = client.droplets.list()
    volumes = client.volumes.list()
    domains = client.domains.list()

    console.print("\n[bold]Resources:[/bold]")
    console.print(f"  Droplets: {len(droplets.get('droplets', []))}")
    console.print(f"  Volumes: {len(volumes.get('volumes', []))}")
    console.print(f"  Domains: {len(domains.get('domains', []))}")
    console.print()


if __name__ == "__main__":
    app()

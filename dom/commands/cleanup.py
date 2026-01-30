"""Cleanup commands - find orphaned or unused resources."""

import typer
from rich.console import Console
from rich.table import Table

from dom.utils import get_client

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("all")
def cleanup_all(
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Show what would be cleaned up"),
):
    """Find all orphaned and unused resources."""
    client = get_client()

    console.print("\n[bold]Cleanup Analysis[/bold]")
    if dry_run:
        console.print("[yellow]DRY RUN - no changes will be made[/yellow]\n")

    issues_found = False

    # Unattached volumes
    volumes = client.volumes.list().get("volumes", [])
    unattached = [v for v in volumes if not v.get("droplet_ids")]

    if unattached:
        issues_found = True
        table = Table(title="Unattached Volumes")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Size (GB)")
        table.add_column("Monthly Cost", justify="right")

        total_cost = 0
        for v in unattached:
            cost = v["size_gigabytes"] * 0.10
            total_cost += cost
            table.add_row(v["id"], v["name"], str(v["size_gigabytes"]), f"${cost:.2f}")

        console.print(table)
        console.print(f"[yellow]Potential savings: ${total_cost:.2f}/month[/yellow]\n")

    # Unused snapshots (older than 90 days)
    try:
        snapshots = client.snapshots.list().get("snapshots", [])
        # Could add age filtering here
        if snapshots:
            console.print(f"[dim]Found {len(snapshots)} snapshots - review manually[/dim]")
    except Exception:
        pass

    # Unused SSH keys (not attached to any droplet)
    # This is harder to detect accurately, skip for now

    # Floating IPs not attached
    try:
        floating_ips = client.floating_ips.list().get("floating_ips", [])
        unassigned = [ip for ip in floating_ips if not ip.get("droplet")]

        if unassigned:
            issues_found = True
            table = Table(title="Unassigned Floating IPs")
            table.add_column("IP", style="cyan")
            table.add_column("Region")

            for ip in unassigned:
                table.add_row(ip["ip"], ip["region"]["slug"])

            console.print(table)
            console.print("[yellow]Floating IPs cost $5/month when not attached[/yellow]\n")
    except Exception:
        pass

    # Load balancers with no backends
    try:
        lbs = client.load_balancers.list().get("load_balancers", [])
        empty_lbs = [lb for lb in lbs if not lb.get("droplet_ids")]

        if empty_lbs:
            issues_found = True
            table = Table(title="Load Balancers with No Backends")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Region")

            for lb in empty_lbs:
                table.add_row(lb["id"], lb["name"], lb["region"])

            console.print(table)
            console.print("[yellow]Load balancers cost $12+/month[/yellow]\n")
    except Exception:
        pass

    if not issues_found:
        console.print("[green]No obvious cleanup opportunities found![/green]\n")


@app.command("volumes")
def cleanup_volumes(
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Show vs actually delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Find and optionally delete unattached volumes."""
    client = get_client()

    volumes = client.volumes.list().get("volumes", [])
    unattached = [v for v in volumes if not v.get("droplet_ids")]

    if not unattached:
        console.print("[green]No unattached volumes found[/green]")
        return

    table = Table(title="Unattached Volumes")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Size (GB)")
    table.add_column("Region")
    table.add_column("Created")

    for v in unattached:
        table.add_row(
            v["id"],
            v["name"],
            str(v["size_gigabytes"]),
            v["region"]["slug"],
            v["created_at"][:10],
        )

    console.print(table)

    if dry_run:
        console.print("\n[yellow]DRY RUN - use --execute to delete[/yellow]")
        return

    if not force:
        confirm = typer.confirm(f"Delete {len(unattached)} volumes?")
        if not confirm:
            console.print("[dim]Aborted[/dim]")
            return

    for v in unattached:
        try:
            client.volumes.delete(v["id"])
            console.print(f"[green]Deleted:[/green] {v['name']}")
        except Exception as e:
            console.print(f"[red]Failed to delete {v['name']}:[/red] {e}")


@app.command("snapshots")
def cleanup_snapshots(
    days: int = typer.Option(90, "--older-than", "-d", help="Delete snapshots older than N days"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Show vs actually delete"),
):
    """Find old snapshots."""
    from datetime import datetime, timedelta, timezone

    client = get_client()

    snapshots = client.snapshots.list().get("snapshots", [])

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    old_snapshots = []

    for s in snapshots:
        created = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))
        if created < cutoff:
            old_snapshots.append(s)

    if not old_snapshots:
        console.print(f"[green]No snapshots older than {days} days[/green]")
        return

    table = Table(title=f"Snapshots older than {days} days")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Size (GB)")
    table.add_column("Created")

    for s in old_snapshots:
        table.add_row(
            s["id"],
            s["name"],
            str(s["min_disk_size"]),
            s["created_at"][:10],
        )

    console.print(table)

    if dry_run:
        console.print(f"\n[yellow]DRY RUN - found {len(old_snapshots)} old snapshots[/yellow]")

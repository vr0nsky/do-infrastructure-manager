"""Audit commands - list and inspect DigitalOcean resources."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from dom.utils import get_client

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("all")
def audit_all():
    """List all resources in your account."""
    client = get_client()

    console.print("\n[bold]DigitalOcean Resource Audit[/bold]\n")

    # Droplets
    console.print("[bold cyan]Droplets[/bold cyan]")
    try:
        droplets = client.droplets.list().get("droplets", [])
        if droplets:
            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Region")
            table.add_column("Size")
            table.add_column("IP")
            table.add_column("Status")

            for d in droplets:
                ip = d["networks"]["v4"][0]["ip_address"] if d["networks"]["v4"] else "-"
                table.add_row(
                    str(d["id"]),
                    d["name"],
                    d["region"]["slug"],
                    d["size_slug"],
                    ip,
                    d["status"],
                )
            console.print(table)
        else:
            console.print("[dim]  No droplets found[/dim]")
    except Exception as e:
        console.print(f"[red]  Error: {e}[/red]")

    # Volumes
    console.print("\n[bold cyan]Volumes[/bold cyan]")
    try:
        volumes = client.volumes.list().get("volumes", [])
        if volumes:
            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Size (GB)")
            table.add_column("Region")
            table.add_column("Attached To")

            for v in volumes:
                attached = ", ".join(str(d) for d in v.get("droplet_ids", [])) or "-"
                table.add_row(
                    v["id"],
                    v["name"],
                    str(v["size_gigabytes"]),
                    v["region"]["slug"],
                    attached,
                )
            console.print(table)
        else:
            console.print("[dim]  No volumes found[/dim]")
    except Exception as e:
        console.print(f"[red]  Error: {e}[/red]")

    # Domains
    console.print("\n[bold cyan]Domains[/bold cyan]")
    try:
        domains = client.domains.list().get("domains", [])
        if domains:
            for domain in domains:
                console.print(f"  - {domain['name']}")
        else:
            console.print("[dim]  No domains found[/dim]")
    except Exception as e:
        console.print(f"[red]  Error: {e}[/red]")

    # Firewalls
    console.print("\n[bold cyan]Firewalls[/bold cyan]")
    try:
        firewalls = client.firewalls.list().get("firewalls", [])
        if firewalls:
            for fw in firewalls:
                console.print(f"  - {fw['name']} ({len(fw.get('droplet_ids', []))} droplets)")
        else:
            console.print("[dim]  No firewalls found[/dim]")
    except Exception as e:
        console.print(f"[red]  Error: {e}[/red]")

    # Load Balancers
    console.print("\n[bold cyan]Load Balancers[/bold cyan]")
    try:
        lbs = client.load_balancers.list().get("load_balancers", [])
        if lbs:
            for lb in lbs:
                console.print(f"  - {lb['name']} ({lb['ip']}) - {lb['status']}")
        else:
            console.print("[dim]  No load balancers found[/dim]")
    except Exception as e:
        console.print(f"[red]  Error: {e}[/red]")

    # Databases
    console.print("\n[bold cyan]Database Clusters[/bold cyan]")
    try:
        databases = client.databases.list_clusters().get("databases", [])
        if databases:
            table = Table()
            table.add_column("Name", style="green")
            table.add_column("Engine")
            table.add_column("Size")
            table.add_column("Region")
            table.add_column("Status")

            for db in databases:
                table.add_row(
                    db["name"],
                    f"{db['engine']} {db['version']}",
                    db["size"],
                    db["region"],
                    db["status"],
                )
            console.print(table)
        else:
            console.print("[dim]  No database clusters found[/dim]")
    except Exception as e:
        console.print(f"[red]  Error: {e}[/red]")

    # Kubernetes
    console.print("\n[bold cyan]Kubernetes Clusters[/bold cyan]")
    try:
        clusters = client.kubernetes.list_clusters().get("kubernetes_clusters", [])
        if clusters:
            table = Table()
            table.add_column("Name", style="green")
            table.add_column("Region")
            table.add_column("Version")
            table.add_column("Nodes")
            table.add_column("Status")

            for k in clusters:
                node_count = sum(p["count"] for p in k.get("node_pools", []))
                table.add_row(
                    k["name"],
                    k["region"],
                    k["version"],
                    str(node_count),
                    k["status"]["state"],
                )
            console.print(table)
        else:
            console.print("[dim]  No kubernetes clusters found[/dim]")
    except Exception as e:
        console.print(f"[red]  Error: {e}[/red]")

    # Apps (App Platform)
    console.print("\n[bold cyan]Apps (App Platform)[/bold cyan]")
    try:
        apps = client.apps.list().get("apps", [])
        if apps:
            for app in apps:
                console.print(f"  - {app['spec']['name']} - {app.get('live_url', 'no url')}")
        else:
            console.print("[dim]  No apps found[/dim]")
    except Exception as e:
        console.print(f"[red]  Error: {e}[/red]")

    # Spaces (object storage buckets)
    console.print("\n[bold cyan]Spaces[/bold cyan]")
    console.print("[dim]  (Spaces API not supported by pydo - use s3cmd or doctl)[/dim]")

    console.print()


@app.command("droplets")
def audit_droplets(
    region: Optional[str] = typer.Option(None, "--region", "-r", help="Filter by region"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """List all droplets with details."""
    client = get_client()

    params = {}
    if tag:
        params["tag_name"] = tag

    droplets = client.droplets.list(**params).get("droplets", [])

    if region:
        droplets = [d for d in droplets if d["region"]["slug"] == region]

    if not droplets:
        console.print("[dim]No droplets found[/dim]")
        return

    table = Table(title="Droplets")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Region")
    table.add_column("Size")
    table.add_column("vCPUs")
    table.add_column("Memory")
    table.add_column("Disk")
    table.add_column("IP")
    table.add_column("Status")
    table.add_column("Tags")

    for d in droplets:
        ip = d["networks"]["v4"][0]["ip_address"] if d["networks"]["v4"] else "-"
        tags = ", ".join(d.get("tags", [])) or "-"
        table.add_row(
            str(d["id"]),
            d["name"],
            d["region"]["slug"],
            d["size_slug"],
            str(d["vcpus"]),
            f"{d['memory']} MB",
            f"{d['disk']} GB",
            ip,
            d["status"],
            tags,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(droplets)} droplets[/dim]\n")


@app.command("domains")
def audit_domains():
    """List all domains and DNS records."""
    client = get_client()

    domains = client.domains.list().get("domains", [])

    if not domains:
        console.print("[dim]No domains found[/dim]")
        return

    for domain in domains:
        console.print(f"\n[bold]{domain['name']}[/bold]")

        records = client.domains.list_records(domain["name"]).get("domain_records", [])

        if records:
            table = Table()
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Data")
            table.add_column("TTL")

            for r in records:
                table.add_row(
                    r["type"],
                    r["name"],
                    r["data"],
                    str(r["ttl"]),
                )
            console.print(table)

    console.print()


@app.command("firewalls")
def audit_firewalls():
    """List all firewalls and their rules."""
    client = get_client()

    firewalls = client.firewalls.list().get("firewalls", [])

    if not firewalls:
        console.print("[dim]No firewalls found[/dim]")
        return

    for fw in firewalls:
        console.print(f"\n[bold]{fw['name']}[/bold] ({fw['id']})")
        console.print(f"  Droplets: {len(fw.get('droplet_ids', []))}")

        # Inbound rules
        inbound = fw.get("inbound_rules", [])
        if inbound:
            console.print("  [green]Inbound:[/green]")
            for rule in inbound:
                sources = rule.get("sources", {})
                src = sources.get("addresses", sources.get("droplet_ids", ["any"]))
                console.print(f"    {rule['protocol']}:{rule['ports']} from {src}")

        # Outbound rules
        outbound = fw.get("outbound_rules", [])
        if outbound:
            console.print("  [yellow]Outbound:[/yellow]")
            for rule in outbound:
                destinations = rule.get("destinations", {})
                dst = destinations.get("addresses", destinations.get("droplet_ids", ["any"]))
                console.print(f"    {rule['protocol']}:{rule['ports']} to {dst}")

    console.print()

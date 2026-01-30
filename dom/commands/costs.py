"""Cost analysis commands."""

from typing import Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table

from dom.utils import get_client

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command("summary")
def cost_summary():
    """Show current month-to-date balance and usage."""
    client = get_client()

    balance = client.balance.get()["balance"] if hasattr(client, 'balance') else None

    if balance:
        console.print("\n[bold]Account Balance[/bold]\n")
        console.print(f"  Month-to-date balance: ${balance.get('month_to_date_balance', 'N/A')}")
        console.print(f"  Account balance: ${balance.get('account_balance', 'N/A')}")
        console.print(f"  Month-to-date usage: ${balance.get('month_to_date_usage', 'N/A')}")
        console.print(f"  Generated at: {balance.get('generated_at', 'N/A')}")
    else:
        console.print("[yellow]Balance API not available[/yellow]")

    console.print()


@app.command("estimate")
def cost_estimate():
    """Estimate monthly costs based on current resources."""
    client = get_client()

    console.print("\n[bold]Estimated Monthly Costs[/bold]\n")

    total = 0.0

    # Droplet costs (approximate based on common sizes)
    size_prices = {
        "s-1vcpu-512mb-10gb": 4,
        "s-1vcpu-1gb": 6,
        "s-1vcpu-2gb": 12,
        "s-2vcpu-2gb": 18,
        "s-2vcpu-4gb": 24,
        "s-4vcpu-8gb": 48,
        "s-8vcpu-16gb": 96,
    }

    droplets = client.droplets.list().get("droplets", [])
    if droplets:
        table = Table(title="Droplets")
        table.add_column("Name", style="green")
        table.add_column("Size")
        table.add_column("Est. Monthly", justify="right")

        for d in droplets:
            price = size_prices.get(d["size_slug"], 0)
            if price == 0:
                # Try to extract from size_slug pattern
                price = d.get("size", {}).get("price_monthly", 0)
            total += price
            table.add_row(d["name"], d["size_slug"], f"${price:.2f}")

        console.print(table)

    # Volume costs ($0.10 per GB/month)
    volumes = client.volumes.list().get("volumes", [])
    if volumes:
        table = Table(title="\nVolumes ($0.10/GB/month)")
        table.add_column("Name", style="green")
        table.add_column("Size (GB)", justify="right")
        table.add_column("Est. Monthly", justify="right")

        for v in volumes:
            price = v["size_gigabytes"] * 0.10
            total += price
            table.add_row(v["name"], str(v["size_gigabytes"]), f"${price:.2f}")

        console.print(table)

    # Database clusters
    try:
        databases = client.databases.list_clusters().get("databases", [])
        if databases:
            table = Table(title="\nDatabase Clusters")
            table.add_column("Name", style="green")
            table.add_column("Engine")
            table.add_column("Size")
            table.add_column("Est. Monthly", justify="right")

            for db in databases:
                # Approximate prices
                price = 15  # Base price, actual varies
                total += price
                table.add_row(db["name"], db["engine"], db["size"], f"${price:.2f}+")

            console.print(table)
    except Exception:
        pass

    console.print(f"\n[bold]Estimated Total: ${total:.2f}/month[/bold]")
    console.print("[dim]Note: Estimates are approximate. Check billing for actual costs.[/dim]\n")


@app.command("by-tag")
def cost_by_tag():
    """Break down costs by resource tags."""
    client = get_client()

    console.print("\n[bold]Costs by Tag[/bold]\n")

    size_prices = {
        "s-1vcpu-512mb-10gb": 4,
        "s-1vcpu-1gb": 6,
        "s-1vcpu-2gb": 12,
        "s-2vcpu-2gb": 18,
        "s-2vcpu-4gb": 24,
        "s-4vcpu-8gb": 48,
    }

    droplets = client.droplets.list().get("droplets", [])

    tag_costs: dict[str, float] = {}
    untagged = 0.0

    for d in droplets:
        price = size_prices.get(d["size_slug"], 10)
        tags = d.get("tags", [])

        if tags:
            for tag in tags:
                tag_costs[tag] = tag_costs.get(tag, 0) + price
        else:
            untagged += price

    if tag_costs:
        table = Table()
        table.add_column("Tag", style="cyan")
        table.add_column("Est. Monthly", justify="right")

        for tag, cost in sorted(tag_costs.items(), key=lambda x: -x[1]):
            table.add_row(tag, f"${cost:.2f}")

        if untagged > 0:
            table.add_row("[dim]untagged[/dim]", f"${untagged:.2f}")

        console.print(table)
    else:
        console.print("[dim]No tagged resources found[/dim]")

    console.print()

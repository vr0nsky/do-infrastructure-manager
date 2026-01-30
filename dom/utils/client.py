"""DigitalOcean API client wrapper."""

import os
import sys

from pydo import Client
from rich.console import Console

console = Console()


def get_client() -> Client:
    """Get authenticated DigitalOcean client."""
    token = os.getenv("DIGITALOCEAN_TOKEN") or os.getenv("DO_TOKEN")

    if not token:
        console.print(
            "[red]Error:[/red] DIGITALOCEAN_TOKEN or DO_TOKEN environment variable not set.\n"
            "Export your token: export DIGITALOCEAN_TOKEN='your-token-here'"
        )
        sys.exit(1)

    return Client(token=token)


def handle_api_error(func):
    """Decorator to handle API errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            console.print(f"[red]API Error:[/red] {e}")
            sys.exit(1)
    return wrapper

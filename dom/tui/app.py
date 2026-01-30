"""Main TUI Application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label, Button, DataTable
from textual.screen import Screen

from dom.utils import get_client


class DropletDetailScreen(Screen):
    """Screen showing droplet details."""

    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("s", "ssh", "SSH"),
        Binding("r", "reboot", "Reboot"),
    ]

    def __init__(self, droplet: dict):
        super().__init__()
        self.droplet = droplet

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(f"[bold cyan]{self.droplet['name']}[/bold cyan]", classes="title"),
            Static(""),
            Static(f"[bold]ID:[/bold]       {self.droplet['id']}"),
            Static(f"[bold]Status:[/bold]   {self._status_color(self.droplet['status'])}"),
            Static(f"[bold]Region:[/bold]   {self.droplet['region']['slug']} ({self.droplet['region']['name']})"),
            Static(f"[bold]Size:[/bold]     {self.droplet['size_slug']}"),
            Static(f"[bold]vCPUs:[/bold]    {self.droplet['vcpus']}"),
            Static(f"[bold]Memory:[/bold]   {self.droplet['memory']} MB"),
            Static(f"[bold]Disk:[/bold]     {self.droplet['disk']} GB"),
            Static(f"[bold]Image:[/bold]    {self.droplet['image']['slug'] or self.droplet['image']['name']}"),
            Static(""),
            Static(f"[bold]Public IP:[/bold]  {self._get_ip('public')}"),
            Static(f"[bold]Private IP:[/bold] {self._get_ip('private')}"),
            Static(""),
            Static(f"[bold]Tags:[/bold]     {', '.join(self.droplet.get('tags', [])) or '-'}"),
            Static(f"[bold]Created:[/bold]  {self.droplet['created_at'][:10]}"),
            Static(""),
            Horizontal(
                Button("SSH", id="ssh", variant="primary"),
                Button("Reboot", id="reboot", variant="warning"),
                Button("Power Off", id="poweroff", variant="error"),
                classes="buttons",
            ),
            id="detail-container",
        )
        yield Footer()

    def _status_color(self, status: str) -> str:
        colors = {"active": "green", "off": "red", "new": "yellow"}
        color = colors.get(status, "white")
        return f"[{color}]{status}[/{color}]"

    def _get_ip(self, ip_type: str) -> str:
        networks = self.droplet.get("networks", {}).get("v4", [])
        for net in networks:
            if net["type"] == ip_type:
                return net["ip_address"]
        return "-"

    def action_pop_screen(self):
        self.app.pop_screen()

    def action_ssh(self):
        ip = self._get_ip("public")
        if ip != "-":
            self.app.exit(result=f"ssh root@{ip}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ssh":
            self.action_ssh()
        elif event.button.id == "reboot":
            self.notify(f"Reboot {self.droplet['name']}? (not implemented yet)", severity="warning")


class ResourceListScreen(Screen):
    """Main screen with resource list."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "droplets", "Droplets"),
        Binding("v", "volumes", "Volumes"),
        Binding("f", "firewalls", "Firewalls"),
    ]

    def __init__(self):
        super().__init__()
        self.client = None
        self.current_view = "droplets"
        self.resources = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Button("Droplets", id="btn-droplets", variant="primary"),
                Button("Volumes", id="btn-volumes"),
                Button("Domains", id="btn-domains"),
                Button("Firewalls", id="btn-firewalls"),
                Button("Databases", id="btn-databases"),
                classes="nav-buttons",
            ),
            DataTable(id="resource-table"),
            id="main-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.client = get_client()
        self.load_droplets()

    def load_droplets(self) -> None:
        self.current_view = "droplets"
        table = self.query_one("#resource-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns("ID", "Name", "Region", "Size", "IP", "Status")

        try:
            droplets = self.client.droplets.list().get("droplets", [])
            self.resources = droplets
            for d in droplets:
                ip = d["networks"]["v4"][0]["ip_address"] if d["networks"]["v4"] else "-"
                status = d["status"]
                status_display = f"[green]{status}[/]" if status == "active" else f"[red]{status}[/]"
                table.add_row(str(d["id"]), d["name"], d["region"]["slug"], d["size_slug"], ip, status_display)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def load_volumes(self) -> None:
        self.current_view = "volumes"
        table = self.query_one("#resource-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns("ID", "Name", "Size (GB)", "Region", "Attached To")

        try:
            volumes = self.client.volumes.list().get("volumes", [])
            self.resources = volumes
            for v in volumes:
                attached = ", ".join(str(d) for d in v.get("droplet_ids", [])) or "-"
                table.add_row(v["id"][:8], v["name"], str(v["size_gigabytes"]), v["region"]["slug"], attached)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def load_domains(self) -> None:
        self.current_view = "domains"
        table = self.query_one("#resource-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns("Domain", "TTL")

        try:
            domains = self.client.domains.list().get("domains", [])
            self.resources = domains
            for d in domains:
                table.add_row(d["name"], str(d.get("ttl", "-")))
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def load_firewalls(self) -> None:
        self.current_view = "firewalls"
        table = self.query_one("#resource-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns("ID", "Name", "Droplets", "Inbound Rules", "Outbound Rules")

        try:
            firewalls = self.client.firewalls.list().get("firewalls", [])
            self.resources = firewalls
            for fw in firewalls:
                table.add_row(
                    fw["id"][:8],
                    fw["name"],
                    str(len(fw.get("droplet_ids", []))),
                    str(len(fw.get("inbound_rules", []))),
                    str(len(fw.get("outbound_rules", []))),
                )
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def load_databases(self) -> None:
        self.current_view = "databases"
        table = self.query_one("#resource-table", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns("Name", "Engine", "Size", "Region", "Status")

        try:
            databases = self.client.databases.list_clusters().get("databases", [])
            self.resources = databases
            for db in databases:
                table.add_row(
                    db["name"],
                    f"{db['engine']} {db['version']}",
                    db["size"],
                    db["region"],
                    db["status"],
                )
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Reset all buttons
        for btn in self.query(".nav-buttons Button"):
            btn.variant = "default"
        event.button.variant = "primary"

        if event.button.id == "btn-droplets":
            self.load_droplets()
        elif event.button.id == "btn-volumes":
            self.load_volumes()
        elif event.button.id == "btn-domains":
            self.load_domains()
        elif event.button.id == "btn-firewalls":
            self.load_firewalls()
        elif event.button.id == "btn-databases":
            self.load_databases()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if self.current_view == "droplets" and self.resources:
            row_index = event.cursor_row
            if 0 <= row_index < len(self.resources):
                droplet = self.resources[row_index]
                self.app.push_screen(DropletDetailScreen(droplet))

    def action_refresh(self) -> None:
        if self.current_view == "droplets":
            self.load_droplets()
        elif self.current_view == "volumes":
            self.load_volumes()
        elif self.current_view == "domains":
            self.load_domains()
        elif self.current_view == "firewalls":
            self.load_firewalls()
        elif self.current_view == "databases":
            self.load_databases()
        self.notify("Refreshed!")

    def action_droplets(self) -> None:
        self.load_droplets()

    def action_volumes(self) -> None:
        self.load_volumes()

    def action_firewalls(self) -> None:
        self.load_firewalls()


class DOManagerApp(App):
    """DigitalOcean Manager TUI Application."""

    TITLE = "DigitalOcean Manager"
    CSS = """
    #main-container {
        height: 100%;
        padding: 1;
    }

    .nav-buttons {
        height: 3;
        margin-bottom: 1;
    }

    .nav-buttons Button {
        margin-right: 1;
    }

    #resource-table {
        height: 100%;
    }

    #detail-container {
        padding: 2;
    }

    .title {
        text-align: center;
        padding: 1;
    }

    .buttons {
        margin-top: 2;
        height: 3;
    }

    .buttons Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen(ResourceListScreen())


def run_tui():
    """Run the TUI application."""
    app = DOManagerApp()
    result = app.run()
    if result:
        print(f"\nRun: {result}")

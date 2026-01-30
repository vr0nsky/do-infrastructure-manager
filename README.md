# DigitalOcean Infrastructure Manager

CLI tool per gestire, auditare ed esportare l'infrastruttura DigitalOcean esistente.

## Features

- **TUI Interattiva**: interfaccia terminale navigabile con mouse e tastiera
- **Audit**: visualizza tutte le risorse nel tuo account (droplets, volumes, domains, firewalls, databases, k8s)
- **Costs**: stima dei costi mensili e breakdown per tag
- **Cleanup**: trova risorse orfane (volumi non attached, floating IP non assegnati, snapshot vecchi)
- **Export**: genera configurazioni Terraform e inventory Ansible dalle risorse esistenti

## TUI Interattiva

Lancia l'interfaccia interattiva:

```bash
dom tui
```

![TUI Screenshot](docs/tui-screenshot.png)

**Navigazione:**
- `↑/↓` o mouse: naviga nella lista
- `Enter`: dettagli risorsa
- `r`: refresh
- `q`: esci
- Click sui tab: cambia tipo risorsa (Droplets, Volumes, Domains...)

## Quick Start

### 1. Installa

```bash
pip install -e .
```

### 2. Configura il token

```bash
export DIGITALOCEAN_TOKEN="your-token-here"
```

Oppure copia `.env.example` in `.env` e inserisci il token.

### 3. Usa

```bash
# Status account
dom status

# Lista tutte le risorse
dom audit all

# Solo droplets
dom audit droplets

# Stima costi
dom costs estimate

# Trova risorse orfane
dom cleanup all

# Esporta in Terraform
dom export terraform -o ./generated/terraform

# Esporta inventory Ansible
dom export ansible -o ./generated/ansible
```

## Comandi disponibili

```
dom status              # Status account e conteggio risorse
dom version             # Versione del tool

dom audit all           # Tutte le risorse
dom audit droplets      # Solo droplets (con filtri --region, --tag)
dom audit domains       # Domini e record DNS
dom audit firewalls     # Firewall e regole

dom costs summary       # Bilancio attuale
dom costs estimate      # Stima costi mensili
dom costs by-tag        # Costi raggruppati per tag

dom cleanup all         # Trova tutto quello che si può pulire
dom cleanup volumes     # Volumi non attached
dom cleanup snapshots   # Snapshot vecchi (--older-than 90)

dom export terraform    # Genera main.tf + import.sh
dom export ansible      # Genera inventory.ini + inventory.yml

dom tui                 # Interfaccia interattiva
```

## Workflow consigliato

### Importare infrastruttura esistente in Terraform

1. Esporta le risorse:
   ```bash
   dom export terraform -o ./terraform/imported
   ```

2. Rivedi i file generati in `./terraform/imported/`

3. Inizializza Terraform:
   ```bash
   cd terraform
   terraform init
   ```

4. Importa lo state:
   ```bash
   bash imported/import.sh
   ```

5. Verifica:
   ```bash
   terraform plan  # Dovrebbe mostrare "No changes"
   ```

### Gestire con Ansible

1. Esporta l'inventory:
   ```bash
   dom export ansible -o ./ansible/inventory
   ```

2. Testa la connessione:
   ```bash
   ansible -i ansible/inventory/inventory.ini all -m ping
   ```

## Struttura progetto

```
do-infrastructure-manager/
├── dom/                    # CLI Python
│   ├── cli.py              # Entry point
│   ├── commands/           # Sottocomandi
│   │   ├── audit.py
│   │   ├── costs.py
│   │   ├── cleanup.py
│   │   └── export.py
│   ├── tui/                # Interfaccia interattiva
│   │   └── app.py
│   └── utils/
│       └── client.py       # Wrapper pydo
├── terraform/              # Configurazioni Terraform
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── ansible/                # Playbook Ansible
│   ├── inventory/
│   └── playbooks/
├── Makefile                # Shortcuts
└── pyproject.toml          # Package config
```

## Sviluppo

```bash
# Installa in dev mode
make dev

# Lint
make lint

# Test
make test
```

## Requisiti

- Python >= 3.9
- Token API DigitalOcean con permessi di lettura

## License

MIT

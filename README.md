# DigitalOcean Infrastructure Manager

CLI tool per gestire, auditare ed esportare l'infrastruttura DigitalOcean esistente.

## Features

- **TUI Interattiva**: interfaccia terminale navigabile con mouse e tastiera
- **Audit**: visualizza tutte le risorse nel tuo account (droplets, volumes, domains, firewalls, databases, k8s)
- **Costs**: stima dei costi mensili e breakdown per tag
- **Cleanup**: trova risorse orfane (volumi non attached, floating IP non assegnati, snapshot vecchi)
- **Export**: genera configurazioni Terraform e inventory Ansible dalle risorse esistenti
- **Terraform wrapper**: comandi `dom tf` per init, plan, apply, import
- **Ansible wrapper**: comandi `dom ans` per ping, play, shell

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

# Esporta in Terraform (default: ./terraform/generated/)
dom export terraform

# Esporta inventory Ansible (default: ./ansible/inventory/)
dom export ansible
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

dom export terraform    # Genera main.tf + import.sh (in ./terraform/generated/)
dom export ansible      # Genera inventory.ini + inventory.yml (in ./ansible/inventory/)

dom tui                 # Interfaccia interattiva

# Terraform wrapper
dom tf init             # terraform init
dom tf plan             # terraform plan
dom tf apply            # terraform apply
dom tf apply -y         # apply senza conferma
dom tf import           # esegue import.sh generato
dom tf state            # lista risorse nello state

# Ansible wrapper
dom ans ping            # ping tutti gli host
dom ans play <playbook> # esegue un playbook
dom ans shell "uptime"  # comando su tutti gli host
dom ans inventory       # mostra inventory
dom ans playbooks       # lista playbook disponibili
```

## Workflow consigliato

### Importare infrastruttura esistente in Terraform

```bash
# 1. Esporta le risorse
dom export terraform

# 2. Rivedi i file generati in ./terraform/generated/

# 3. Inizializza Terraform
dom tf init

# 4. Importa lo state
dom tf import

# 5. Verifica (dovrebbe mostrare "No changes")
dom tf plan
```

### Gestire con Ansible

```bash
# 1. Esporta l'inventory
dom export ansible

# 2. Testa la connessione
dom ans ping

# 3. Esegui un playbook
dom ans play setup-base

# 4. Esegui un comando su tutti gli host
dom ans shell "df -h"
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
│   │   ├── export.py
│   │   ├── tf.py           # Terraform wrapper
│   │   └── ans.py          # Ansible wrapper
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

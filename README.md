# Black Ops Framework (BOF) 💀

Black Ops is a high-performance, asynchronous red teaming framework designed for security research, reconnaissance, and automated offensive operations.

---

## 🛠️ Architecture
BOF is a modular Python framework designed for speed and extensibility.

*   **Asynchronous Engine:** Utilizes `asyncio` & `aiohttp` for maximum concurrency.
*   **Modular Design:** Easily add new tools by inheriting from `BaseModule`.
*   **Polymorphic Evasion:** Dynamic AST-based payload mutation.
*   **Automated Reporting:** Centralized logging and report generation.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- `docker` (optional, for isolated environments)

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/kalix/BlackOps2
   cd BlackOps2
   ```
2. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configure API Keys:**
   Create a `secrets.json` file in the root directory:
   ```json
   {
     "openai_key": "sk-...",
     "rapidapi_key": "..."
   }
   ```

### Execution
Launch the framework:
```bash
python black_ops.py
```

---

## 🏗️ Project Structure
```text
BlackOps_2.0/
├── src/            # Core framework, modules, and utilities
├── tests/          # Unit and integration tests
├── black_ops.py    # Main entry point
├── README.md
└── requirements.txt
```

---

## ⚡ Core Modules

| Module | Category | Capabilities |
| :--- | :--- | :--- |
| **NetScout Pro** | Recon | Async Port Scan, DNS Enum |
| **DirFuzzer** | Web | Async Path Discovery |
| **VenomMaker** | Offensive | Payload Mutation |
| **AsyncC2** | C2 | Reverse Shell Mgmt |
| **Social Hunter**| OSINT | Metadata Extraction |

---

## 🧪 Development
```bash
# Run tests
pytest tests/

# Run linting & formatting
ruff check .
ruff format .
```

---

## ⚠️ Legal & Ethical Disclaimer
**FOR AUTHORIZED SECURITY RESEARCH ONLY.**
The author and contributors accept no responsibility for misuse.
# BlackOps_2.0

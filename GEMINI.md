# Black Ops - Ultimate Hacking Suite v2.1 💀

## Project Overview
**Black Ops** is a comprehensive Python-based cyber-security framework designed for penetration testers and red teams. It consolidates multiple powerful modules for reconnaissance, offensive operations, stealth, and forensics into a single, centralized command center.

### Core Technologies
- **Language:** Python 3.x
- **CLI Styling:** [colorama](https://pypi.org/project/colorama/)
- **Network & Recon:** [requests](https://pypi.org/project/requests/), [scapy](https://pypi.org/project/scapy/), [dnspython](https://pypi.org/project/dnspython/)
- **Forensics & Metadata:** [exif](https://pypi.org/project/exif/), [exifread](https://pypi.org/project/exifread/)
- **Anonymity:** [stem](https://pypi.org/project/stem/) (Tor)
- **AI Integration:** [openai](https://pypi.org/project/openai/) (GPT-4o)

### Architecture
The project uses a modular architecture where the main entry point (`black_ops.py`) acts as a menu-driven launcher. Each tool is implemented as a separate Python script that can be executed independently or through the main menu.
- `base_module.py`: Contains `BaseModule`, a common base class for modules providing utility functions like permission checks and banners.
- `config.py`: Centralizes configuration settings such as timeouts, API URLs, and default ports.

## Building and Running

### Prerequisites
- **OS:** Kali Linux (preferred) or other Linux distributions.
- **Python:** 3.x
- **System Tools:** `tor`, `aircrack-ng`, `cloudflared` (required for full functionality).

### Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure API Keys:**
   Create a `secrets.json` file in the root directory:
   ```json
   {
     "rapidapi_key": "YOUR_BREACHDIRECTORY_KEY",
     "openai_key": "YOUR_OPENAI_KEY"
   }
   ```
   Alternatively, set environment variables (refer to `config.py` for details).

### Execution
- **Launch the Framework:**
  ```bash
  sudo python black_ops.py
  ```
  *Note: Root privileges are required for modules that interact with network interfaces or system logs.*

- **Run Individual Modules:**
  Modules can be run directly from the terminal (e.g., `python netscout.py target.com`).

## Development Conventions

### Module Structure
New modules should ideally follow the pattern established in `BaseModule`:
- Inherit from `BaseModule`.
- Implement a `banner()` method for visual consistency.
- Implement a `run()` method for interactive usage.
- Support CLI arguments for non-interactive use where appropriate (see `netscout.py`).

### Styling & Output
- Use `colorama` for color-coded terminal output (Green for success, Red for errors, Yellow for warnings/prompts, Cyan/Blue for info).
- Maintain consistent banner styling.

### Configuration
- Do not hardcode values; add them to `config.py`.
- Use `get_secret()` from `config.py` to securely retrieve API keys.

### Security & Ethics
- This tool is for **authorized security testing only**.
- Do not log or commit sensitive information (e.g., `secrets.json`).
- Adhere to the MIT license and the legal disclaimer in `README.md`.

# StaffRoot

**StaffRoot** is the Groundstate Technology HR/payroll node: a Windows-first desktop prototype for employee records, time & attendance, payroll runs, reporting, user access, audit history, backup/restore, and employee self-service.

StaffRoot is designed around one architectural rule: **the Groundstate Admin Control Center is the master identity and organization authority**. StaffRoot can still operate standalone for development or disconnected environments, but Control Center integration is the canonical direction.

## Current release

**v0.9.7 — Control-ready prototype**

### Included

- Midnight/cyan Groundstate Control Center-style UI shell
- Admin / HR / Employee role separation
- Employee HR profiles with address, DOB, emergency contact, job/pay data, and SSN-last-four only
- Time & Attendance with employee/date filtering and approval workflow
- Payroll run generation from approved time
- Employee paystub history
- Payroll reports and CSV export
- Local users and employee-account linking
- Audit log
- Backup and restore
- Groundstate Admin Control Center connection settings and employee pull-sync
- PyInstaller no-console Windows packaging
- GitHub validation workflow

## Architecture

```text
Groundstate Admin Control Center
        │
        ├── identity / users / roles
        ├── employees / departments
        ├── app permissions
        │
        └──── StaffRoot
               ├── HR extensions
               ├── time & attendance
               ├── payroll
               ├── paystubs
               └── payroll reporting
```

See `docs/GROUNDSTATE_CONTROL_CENTER_INTEGRATION.md` for the integration contract.

## Development login

```text
username: admin
password: admin123
```

**Change this immediately for any persistent installation.** StaffRoot is a prototype and the development credential is intentionally obvious.

## Run from source

Python 3.12+ is recommended.

```bash
python -m pip install -r requirements.txt
python main.py
```

Windows shortcut: `run_staffroot.bat`

## Local configuration

On first run StaffRoot creates `staffroot.local.json`. It is excluded from Git because it may contain a Control Center credential. A safe template is provided in `staffroot.local.example.json`.

## Build StaffRoot.exe

```bash
python -m pip install -r requirements.txt
pyinstaller StaffRoot.spec
```

The spec uses `console=False`, so the packaged application does not open a command prompt window. StaffRoot also hides the login root while the application shell is active, preventing the prior blank/ghost Tk window.

## Data safety

Local runtime files are intentionally excluded from source control: `staffroot.local.json`, `data/*.db`, `data/backups/`, and build artifacts. Do not commit real employee information, payroll records, credentials, or database backups.

## Validation

```bash
python -m compileall -q .
python -c "from main import init_db; init_db(); print('StaffRoot schema initialized')"
```

## License

StaffRoot is licensed under the **Mozilla Public License 2.0**.

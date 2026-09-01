# StaffRoot

**StaffRoot** is a standalone-first HR/payroll desktop prototype for employee records, time and attendance, payroll runs, reporting, local user access, audit history, backup/restore, and employee self-service.

StaffRoot does not require a Groundstate account, Groundstate Admin Center, cloud service, or external identity server. A normal installation creates and manages local accounts and data entirely on the user's machine.

## Current release

**v0.11.0 — standalone-first identity cleanup**

### Included

- Secure first-run creation of the initial local administrator
- Admin / HR / Employee role separation
- Employee HR profiles with address, DOB, emergency contact, job/pay data, and SSN-last-four only
- Time and attendance with employee/date filtering and approval workflow
- Payroll run generation from approved time
- Employee paystub history
- Payroll reports and CSV export
- Local users and employee-account linking
- Audit log
- Integrity-checked backup and restore with rollback copies
- Optional provider-neutral organization directory sync
- PyInstaller no-console Windows packaging
- GitHub validation workflow

## Operation modes

### Standalone — default

Local accounts, roles, employee records, payroll data, backups, and audit history remain entirely within StaffRoot. No network connection or external identity service is needed.

### Organization-managed — optional

An administrator may explicitly configure an organization identity provider to import basic employee directory information. This integration is disabled by default. Provider outages do not prevent local sign-in or access to locally stored StaffRoot data.

The external provider supplies identity and directory references only. StaffRoot remains authoritative for HR extensions, time entries, pay rates, payroll runs, paystubs, deductions, and reports.

See `docs/OPTIONAL_IDENTITY_INTEGRATION.md`.

## First run

StaffRoot does not ship with shared credentials. The first launch creates the initial local administrator. Passwords must be at least 10 characters and are stored as salted PBKDF2 hashes.

## Run from source

Python 3.12+ is recommended.

```bash
python -m pip install -r requirements.txt
python main.py
```

Windows shortcut: `run_staffroot.bat`

## Local configuration

On first run, StaffRoot creates `staffroot.local.json`. The default configuration is standalone and contains no endpoint or credential. The file is excluded from Git because an administrator may later add an organization identity token.

Existing configurations using the former Admin Center keys are migrated in memory to the provider-neutral format. Saving settings writes only the new keys.

## Build StaffRoot.exe

```bash
python -m pip install -r requirements.txt
pyinstaller StaffRoot.spec
```

The specification uses `console=False`, so the packaged application does not open a command prompt window.

## Data safety

Local runtime files are excluded from source control: `staffroot.local.json`, `data/*.db`, `data/backups/`, and build artifacts. Never commit real employee information, payroll records, credentials, or database backups.

## Validation

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
python -c "from main import init_db; init_db(); print('StaffRoot schema initialized')"
```

## License

StaffRoot is licensed under the **Mozilla Public License 2.0**.

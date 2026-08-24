# Security Policy

StaffRoot is currently a working prototype and should be treated as pre-production software.

## Sensitive data

- Do not commit `staffroot.local.json`, database files, backups, API keys, payroll data, or employee records.
- StaffRoot stores only the final four digits of an SSN in the prototype schema.
- Use HTTPS and short-lived credentials when connecting StaffRoot to a remote Groundstate Admin Control Center.
- Change the default `admin / admin123` development credential immediately on any persistent installation.

## Reporting vulnerabilities

Please use a private GitHub security advisory when available. Do not publish employee information or credentials in public issues.

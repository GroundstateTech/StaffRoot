# Security Policy

StaffRoot is a working prototype and should be treated as pre-production software.

## Sensitive data

- Do not commit `staffroot.local.json`, database files, backups, identity tokens, payroll data, or employee records.
- StaffRoot stores only the final four digits of an SSN in the prototype schema.
- StaffRoot ships without shared default credentials and creates its first local administrator interactively.
- Organization identity integration is optional and disabled by default.
- Use HTTPS, narrowly scoped short-lived tokens, and a trusted network when enabling a remote identity provider.
- An external identity outage must not bypass local authorization or corrupt local HR/payroll data.

## Reporting vulnerabilities

Please use a private GitHub security advisory when available. Do not publish employee information or credentials in public issues.

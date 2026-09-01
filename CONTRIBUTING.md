# Contributing to StaffRoot

StaffRoot is a standalone-first HR/payroll application. Public contributors must be able to install, test, and use it without any Groundstate company service.

## Development principles

1. Keep local accounts and core HR/payroll workflows fully functional offline.
2. Treat organization identity integration as optional and disabled by default.
3. Use provider-neutral interfaces; do not add a required vendor or Groundstate-specific login.
4. Keep payroll-specific records authoritative in StaffRoot.
5. Preserve existing database values during schema or terminology migrations.
6. Never commit employee data, databases, backups, tokens, or local configuration.
7. Run `python -m compileall -q .` and `python -m unittest discover -s tests -v` before opening a pull request.

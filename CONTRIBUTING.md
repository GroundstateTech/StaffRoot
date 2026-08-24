# Contributing to StaffRoot

StaffRoot is a Groundstate Technology workforce/HR node designed around a shared Admin Control Center.

## Development principles

1. Keep StaffRoot usable in standalone mode.
2. Treat the Groundstate Admin Control Center as the source of truth for identity, users, roles, departments, and organization structure.
3. Keep payroll-specific records local to StaffRoot unless an explicit integration contract says otherwise.
4. Never commit employee data, databases, backups, API keys, or local configuration.
5. Run `python -m compileall -q .` and `python -c "from main import init_db; init_db()"` before opening a pull request.

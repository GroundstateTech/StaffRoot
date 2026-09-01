# Changelog

## 0.11.0 - 2026-09-01

- Made standalone local operation the explicit default.
- Replaced Groundstate-specific public integration code and UI with an optional provider-neutral directory connector.
- Preserved legacy configuration and database identity values through compatibility mappings.
- Removed the required-ecosystem language from public documentation.
- Added standalone configuration and identity-client regression tests.


## 0.9.7 - 2026-08-24

- Standardized the Groundstate Control Center-linked application architecture.
- Added Admin Center client and employee synchronization panel.
- Added external employee/user identifiers and synchronization metadata.
- Reworked the desktop shell into the Groundstate midnight/cyan left-navigation UI.
- Preserved standalone operation when the Control Center is unavailable.
- Added role-separated Admin/HR and Employee self-service surfaces.
- Hardened local secret handling by excluding `staffroot.local.json` from Git.
- Added repository validation workflow for compile and database initialization checks.
- Added Windows no-console PyInstaller packaging configuration.
- Added backup/restore, audit, reporting, and deployment documentation.

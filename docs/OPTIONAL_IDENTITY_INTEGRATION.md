# Optional organization identity integration

StaffRoot works completely standalone. This connector exists only for organizations that deliberately want to import employee directory information from another system.

## Authority boundaries

StaffRoot always owns:

- local accounts and StaffRoot roles;
- HR details and emergency contacts;
- time and attendance;
- pay rates and schedules;
- payroll runs, paystubs, deductions, and reports;
- local audit history and backups.

An optional identity provider may supply:

- an external subject/employee identifier;
- name and work contact information;
- department and position;
- employment status.

Importing a directory record does not automatically create a StaffRoot login or grant payroll permissions.

## Configuration

The connector is disabled by default:

```json
{
  "identity_provider_name": "",
  "identity_base_url": "",
  "identity_api_token": "",
  "identity_sync_enabled": false
}
```

StaffRoot currently expects provider endpoints for `GET /api/health` and `GET /api/employees`. Treat this as a provisional adapter contract. A future release should prefer OpenID Connect for authentication and SCIM-compatible provisioning where practical.

## Failure behavior

- Missing configuration leaves StaffRoot in standalone mode.
- Connection failures are shown to the administrator and do not block local sign-in.
- Imported records keep their local StaffRoot data when a provider is unavailable.
- Provider tokens stay in the ignored local configuration file.
- Provider responses are JSON-decoded with a two-megabyte response limit.

## Existing installations

The application recognizes legacy Admin Center configuration keys and maps them to the provider-neutral settings. Existing SQLite column names remain physically unchanged for compatibility, while application code exposes them as generic external identity fields. No employee or user identity value is discarded.

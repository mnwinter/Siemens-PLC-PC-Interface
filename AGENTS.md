# Project instructions

Read `PROJECT_INFORMATION.md`, `README.md`, and the relevant file under
`docs/` before changing the interface.

## Controls constraints

- Preserve the validated DB14 memory contract unless a coordinated PLC and PC
  migration is explicitly requested.
- Keep the PLC IP address configurable. Do not hard-code a new site address.
- Never write physical `%I` or `%Q` addresses from a test utility.
- PC-owned and PLC-owned fields must remain separate.
- Any utility that writes PLC memory must require an explicit `--execute`
  argument and must state its exact write scope.
- Restore temporary test values when a diagnostic ends, including after an
  exception whenever communication still permits restoration.
- Do not issue CPU RUN, STOP, reset, download, or hardware-configuration
  commands.
- Treat heartbeat timeout handling as a required fail-safe before controlling
  simulated machine outputs.

## Repository constraints

- Commit source and documentation, not generated EXEs, ZIP files, virtual
  environments, credentials, or customer project archives.
- Keep changes small and testable.
- Record newly proven hardware behavior in `PROJECT_INFORMATION.md`.
- Clearly distinguish tested behavior from proposed architecture.

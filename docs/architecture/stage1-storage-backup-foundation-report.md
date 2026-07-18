# ATLAS Stage 1 Storage And Backup Foundation Report

Date: 2026-07-18

Status: initial foundation implemented.

## Implemented

1. Hardened MVP JSON storage.
   - Added a per-instance reentrant lock in `database/json_database.py`.
   - Writes now use a temporary file and `os.replace`.
   - Collection names with no safe characters are rejected.

2. Added sanitized backup utility.
   - Script: `scripts/create_data_backup.py`
   - Creates ZIP archives for explicit data directories.
   - Adds `backup_manifest.json` with file paths, sizes, SHA-256 checksums, source roots, and timestamp.
   - Skips `.env`, `.env.local`, `.git`, `__pycache__`, `.pytest_cache`, `.pyc`, `.pyo`, `.log`, and `.tmp`.

3. Added tests.
   - `tests/test_json_database.py`
   - `tests/test_backup_script.py`

## Local Backup Created

Created with:

```bash
py -3.12 scripts/create_data_backup.py --output D:\ATLAS_EWU_DATA_BACKUP_20260718-181741.zip --source D:\ATLAS_EWU\data --source D:\ATLAS_EWU\EWU_Data --source D:\ATLAS_EWU\ewu_bot\EWU_Data
```

Result:

- Archive: `D:\ATLAS_EWU_DATA_BACKUP_20260718-181741.zip`
- Archive size: `131691` bytes.
- Included files: `28`.
- Missing optional local sources:
  - `D:\ATLAS_EWU\EWU_Data`
  - `D:\ATLAS_EWU\ewu_bot\EWU_Data`

## Important Boundaries

This does not replace PostgreSQL. It only makes the current MVP JSON storage safer while the project is still on the free Render setup.

This does not automatically download Render persistent disk data. For production-grade backup, the same script should run in an environment that can read `/var/data`, or a Render admin backup/export flow should be added.

## Remaining Work

- Move business data from JSON files to PostgreSQL.
- Add schema migrations.
- Add scheduled encrypted backups for `/var/data`.
- Add restore script and monthly restore drill.
- Add admin-only production backup download or secure offsite upload.
- Define retention policy for backups containing personal data.

## Verification

Commands run locally:

```bash
py -3.12 -m compileall -q api core database services scripts tests
py -3.12 -m unittest discover -s tests
py -3.12 scripts/create_data_backup.py --output D:\ATLAS_EWU_DATA_BACKUP_20260718-181741.zip --source D:\ATLAS_EWU\data --source D:\ATLAS_EWU\EWU_Data --source D:\ATLAS_EWU\ewu_bot\EWU_Data
```

Result:

- Full unittest suite: passed, 36 tests.
- Backup archive created successfully.


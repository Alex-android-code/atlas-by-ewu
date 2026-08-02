# ATLAS Backup And Recovery

## What To Back Up

- JSON database: `$ATLAS_DATA_DIR/db`
- Private uploads: `$ATLAS_DATA_DIR/private_uploads`
- Public operational uploads: `$ATLAS_DATA_DIR/uploads`
- EWU bot runtime data: `$EWU_DATA_DIR`
- Render environment variable inventory, without exposing secret values
- GitHub repository source

## Frequency

- Daily: database and upload metadata.
- Daily: EWU bot leads/PDF metadata.
- Weekly: full `/var/data` archive.
- Monthly: restore drill to a staging/local environment.

## Local Backup Example

```powershell
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Compress-Archive -Path "D:\ATLAS_EWU\data\*" -DestinationPath "D:\ATLAS_BACKUPS\atlas-data-$stamp.zip"
```

Never include `.env` in a shared backup archive.

## Restore Procedure

1. Stop the application.
2. Copy backup data into the target `ATLAS_DATA_DIR`.
3. Verify file permissions.
4. Start the application.
5. Check `/api/health`.
6. Run a read-only smoke test: dashboard, onboarding session, file metadata, and EWU bot health.

## Incident Procedure

1. Preserve logs and current data snapshot.
2. Rotate exposed credentials if incident involves secrets.
3. Restore the last known-good backup to staging.
4. Compare record counts and critical entities.
5. Restore production only after verification.
6. Document incident timeline and follow-up controls.

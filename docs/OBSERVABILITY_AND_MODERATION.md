# ATLAS observability and vacancy moderation

## Environment variables

Set these only in the deployment environment. Do not hard-code IDs in source files.

- `NEXT_PUBLIC_GA_MEASUREMENT_ID` or `GA_MEASUREMENT_ID`: Google Analytics 4 measurement ID.
- `NEXT_PUBLIC_CLARITY_PROJECT_ID` or `CLARITY_PROJECT_ID`: Microsoft Clarity project ID.
- `NEXT_PUBLIC_SENTRY_DSN` or `SENTRY_DSN`: Sentry browser DSN.
- `ATLAS_ADMIN_TOKEN`: optional API token for admin analytics routes when cookie auth is not available.

## Privacy rules

The browser tracker and backend event endpoint remove personal fields before saving or sending analytics:

- names;
- email;
- phone;
- document fields;
- passwords;
- tokens.

Events should use operational parameters only: page, language, user_role, vacancy_id, vacancy_source, profession, country, city, form_step, device_type, and traffic_source.

## Vacancy flow

New vacancies are no longer published automatically.

1. Creation saves the vacancy as `pending_review`.
2. ATLAS runs automatic completeness and duplicate checks.
3. Admin or coordinator reviews warnings.
4. Admin verifies and publishes, or rejects with a reason.

Supported statuses:

- `draft`
- `pending_review`
- `verified`
- `published`
- `rejected`
- `expired`
- `archived`

## Admin routes

- `GET /api/admin/analytics`
- `GET /api/admin/first-vacancies-report`
- `POST /api/admin/vacancies/{vacancy_id}/publish`

Admin routes require `atlas_role=owner|admin` cookie or `x-atlas-admin-token` matching `ATLAS_ADMIN_TOKEN`.

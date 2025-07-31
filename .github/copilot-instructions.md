# Copilot Instructions for Staff Party Lucky Draw Web App

## Project Overview
- This is a Django web app for managing staff check-ins and running a lucky draw during a 2-day event.
- Key features: staff upload (Excel/CSV), QR code generation, check-in via QR scan, live lucky draw (5 winners per day), admin dashboard, and reporting.
- All business logic is in the `lucky_draw` app. The project root is `staff_party`.

## Architecture & Data Flow
- Models: `Staff`, `CheckIn`, `Winner`, `EventSettings` (see `lucky_draw/models.py`).
  - `Staff` has name, department, day, and QR code image.
  - `CheckIn` records staff check-ins per day (unique per staff/day).
  - `Winner` records lucky draw winners per day, with draw order (max 5 per day enforced in view logic).
- Views: All main logic in `lucky_draw/views.py`.
  - `draw_winner` view (POST `/draw-winner/`) ensures only 5 winners per day, only checked-in staff are eligible, and prevents duplicates.
  - QR code generation is automatic on staff creation.
- Templates: Located in `lucky_draw/templates/lucky_draw/`.
- Media: QR codes stored in `media/qr_codes/`.
- Static: CSS/JS in `static/`.

## Developer Workflows
- **Setup:**
  - Install Python 3.8+, pip, and dependencies (`django`, `pillow`, `qrcode`, `openpyxl`, `pandas`).
  - Use `python manage.py makemigrations` and `python manage.py migrate` to set up the database.
  - Run with `python manage.py runserver`.
- **Resetting Database:**
  - Delete `db.sqlite3` and migration files in `lucky_draw/migrations/0*.py`, then re-run migrations.
- **Admin Login:**
  - Fixed credentials: `hr_admin` / `staff_party_2024`.
- **Testing:**
  - No explicit test suite; manual testing via UI and sample CSV (`sample_staff_list.csv`).

## Project Conventions & Patterns
- QR code data format: `staff_id:day` (used for check-in validation).
- All staff uploads must include headers: `Staff Name`, `Department`, `Day 1`.
- Only checked-in staff are eligible for draws; draws limited to 5 per day (enforced in `draw_winner`).
- AJAX/JSON endpoints for QR scan and draw actions.
- Security: CSRF protection, input validation, and unique constraints on check-ins/winners.

## Integration Points
- Uses `qrcode` and `pillow` for QR code image generation.
- Uses `openpyxl`/`pandas` for Excel/CSV parsing.
- No external APIs or microservices.

## Key Files & Directories
- `lucky_draw/models.py`: Data models and QR code logic
- `lucky_draw/views.py`: All business logic and endpoints
- `lucky_draw/forms.py`: Upload and scan forms
- `lucky_draw/urls.py`: App routes
- `staff_party/urls.py`: Project routes
- `media/qr_codes/`: Generated QR images
- `sample_staff_list.csv`: Example upload file

## Example: Drawing a Winner
- POST to `/draw-winner/` with `{ "day": 1 }` (or 2)
- Response includes winner info or error if 5 winners already drawn or no eligible staff

---
For more, see `README.md` and code comments in each file.

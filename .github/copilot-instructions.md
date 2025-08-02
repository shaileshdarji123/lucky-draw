
# Copilot Instructions for Staff Party Lucky Draw Web App

## Project Overview
- Django web app for staff check-in and lucky draw during a 2-day event.
- Features: staff upload (Excel/CSV), QR code generation (on-the-fly), check-in via QR scan, live lucky draw (5 winners/day), admin dashboard, reporting.
- All business logic is in the `lucky_draw` app. Project root is `staff_party`.

## Architecture & Data Flow
- **Models** (`lucky_draw/models.py`): `Staff`, `CheckIn`, `Winner`, `EventSettings`.
  - `Staff`: name, department, day. QR codes are generated on download, not stored.
  - `CheckIn`: unique per staff/day.
  - `Winner`: up to 5 per day, draw order tracked.
- **Views** (`lucky_draw/views.py`): All main logic.
  - `draw_winner` (POST `/draw-winner/`): Only 5 winners/day, only checked-in staff, no duplicates.
  - QR code generation is on-the-fly in download view.
- **Templates**: `lucky_draw/templates/lucky_draw/`
- **Media**: No QR code files stored; media folder only for uploads if needed.
- **Static**: CSS/JS in `static/`

## Developer Workflows
- **Setup**:
  - Python 3.8+, pip, dependencies: `django`, `pillow`, `qrcode`, `openpyxl`, `pandas`, `python-dotenv`, `pymysql` (not `mysqlclient`).
  - Add to `settings.py`:
    ```python
    import pymysql
    pymysql.install_as_MySQLdb()
    ```
  - `python manage.py makemigrations` and `python manage.py migrate`
  - Run: `python manage.py runserver`
- **Reset Database**:
  - Delete `db.sqlite3` and migration files in `lucky_draw/migrations/0*.py`, then re-run migrations.
- **Admin Login**: `hr_admin` / `staff_party_2024`
- **Testing**: Manual via UI and `sample_staff_list.csv`

## Project Conventions & Patterns
- Staff upload files must have headers: `Staff Name`, `Department`, `Day 1`
- QR code data format: `staff_id:day`
- Only checked-in staff eligible for draws; max 5 winners/day (enforced in view logic)
- AJAX/JSON endpoints for QR scan and draw actions
- Security: CSRF protection, input validation, unique constraints on check-ins/winners

## Integration Points
- QR code generation: `qrcode`, `pillow`
- Excel/CSV parsing: `openpyxl`, `pandas`
- Database: MySQL via `PyMySQL` (not `mysqlclient`)
- No external APIs or microservices

## Key Files & Directories
- `lucky_draw/models.py`: Data models
- `lucky_draw/views.py`: Business logic, endpoints
- `lucky_draw/forms.py`: Upload/scan forms
- `lucky_draw/urls.py`: App routes
- `staff_party/urls.py`: Project routes
- `sample_staff_list.csv`: Example upload file

## Example: Drawing a Winner
- POST to `/draw-winner/` with `{ "day": 1 }` or `{ "day": 2 }`
- Response: winner info or error if 5 winners already drawn or no eligible staff

## Additional Notes
- QR scanning works best in Chrome; requires HTTPS in production or localhost for dev.
- For production: set `DEBUG = False`, use MySQL, configure static/media, enable HTTPS.

---
For more, see `README.md` and code comments in each file.

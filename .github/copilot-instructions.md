

# Copilot Instructions for Staff Party Lucky Draw Web App

## Project Overview
- Django web app for staff check-in and lucky draw during a 2-day event.
- Features: staff upload (Excel/CSV), QR code generation (SVG, on-the-fly), check-in via QR scan, live lucky draw (5 winners/day), admin dashboard, reporting.
- All business logic is in the `lucky_draw` app. Project root is `staff_party`.

## Architecture & Data Flow
- **Models** (`lucky_draw/models.py`): `Staff`, `CheckIn`, `Winner`, `EventSettings`.
  - `Staff`: name, department, day. QR codes are generated on download, not stored.
  - `CheckIn`: unique per staff/day.
  - `Winner`: up to 5 per day, draw order tracked.
- **Views** (`lucky_draw/views.py`): All main logic.
  - `draw_winner` (POST `/draw-winner/`): Only 5 winners/day, only checked-in staff, no duplicates.
  - QR code generation is on-the-fly in download view, now using SVG for lightweight hosting.
- **Templates**: `lucky_draw/templates/lucky_draw/` (UI, AJAX endpoints)
- **Static**: CSS/JS in `static/` (Lottie animations, winner_announce.js)
- **Media**: Only for uploads; QR codes are never stored.

## Developer Workflows
- **Setup**:
  - Python 3.8+, pip, dependencies: `django`, `qrcode[svg]`, `openpyxl`, `pandas`, `python-dotenv`, `pymysql` (not `mysqlclient`).
  - Add to `settings.py`:
    ```python
    import pymysql
    pymysql.install_as_MySQLdb()
    ```
  - `python manage.py makemigrations` and `python manage.py migrate`
  - Run: `python manage.py runserver`
- **Static Files (Production/cPanel)**:
  - Set `STATIC_URL = '/static/'`, `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')` in `settings.py`.
  - Run `python manage.py collectstatic` after any static file change.
  - Ensure web server serves files from `staticfiles/`.
- **Reset Database**:
  - Delete `db.sqlite3` and migration files in `lucky_draw/migrations/0*.py`, then re-run migrations.
- **Admin Login**: `hr_admin` / `staff_party_2024`
- **Testing**: Manual via UI and `sample_staff_list_450.csv` (for stress testing)

## Project Conventions & Patterns
- Staff upload files must have headers: `Staff Name`, `Department`, `Day 1`
- QR code data format: `staff_id:day` (SVG, not PNG)
- Only checked-in staff eligible for draws; max 5 winners/day (enforced in view logic)
- AJAX/JSON endpoints for QR scan and draw actions
- Security: CSRF protection, input validation, unique constraints on check-ins/winners
- Winner animation: Lottie JSON in `static/lottie/`, triggered by `winner_announce.js`

## Integration Points
- QR code generation: `qrcode[svg]` (no Pillow)
- Excel/CSV parsing: `openpyxl`, `pandas`
- Database: MySQL via `PyMySQL` (not `mysqlclient`)
- No external APIs or microservices

## Key Files & Directories
- `lucky_draw/models.py`: Data models
- `lucky_draw/views.py`: Business logic, endpoints
- `lucky_draw/forms.py`: Upload/scan forms
- `lucky_draw/urls.py`: App routes
- `staff_party/urls.py`: Project routes
- `static/js/winner_announce.js`: Winner animation logic
- `static/lottie/win_result_1.json`: Lottie animation file
- `sample_staff_list_450.csv`: Example upload file for stress testing

## Example: Drawing a Winner
- POST to `/draw-winner/` with `{ "day": 1 }` or `{ "day": 2 }`
- Response: winner info or error if 5 winners already drawn or no eligible staff

## Additional Notes
- QR scanning works best in Chrome; requires HTTPS in production or localhost for dev.
- For production: set `DEBUG = False`, use MySQL, configure static/media, enable HTTPS.
- For cPanel: always run `collectstatic` and verify static file serving.

---
For more, see `README.md` and code comments in each file.

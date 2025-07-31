# Staff Party Lucky Draw Web App

A Django-based web application for managing staff check-ins and running lucky draws during a 2-day staff party event.

## Features

### 🔐 Authentication
- Fixed HR Admin login (username: `hr_admin`, password: `staff_party_2024`)
- Secure session management

### 📋 Staff Management
- Upload staff list via Excel/CSV files
- Automatic QR code generation for each staff member
- Support for multiple departments and attendance days

### 📱 QR Code System
- Generate unique QR codes for each staff member
- QR codes encode staff ID and attendance day
- Download QR codes for distribution to staff

### ✅ Check-in System
- Real-time QR code scanning using device camera
- Prevent duplicate check-ins
- Mobile-friendly interface for on-site use
- Instant feedback on check-in status

### 🎁 Lucky Draw
- Live lucky draw functionality
- 5 winners per day (drawn one at a time)
- Only checked-in staff eligible for draws
- Separate draws for Day 1 and Day 2
- Real-time winner display

### 📊 Dashboard & Reports
- Real-time statistics (total staff, check-ins, winners)
- View all check-ins by day
- View all lucky draw winners
- Clean, modern UI with responsive design

## File Format Requirements

Upload files should have the following format:

| Staff Name | Department | Day 1 |
|------------|------------|-------|
| John Doe   | F&B        | 1     |
| Jane Smith | Front Office| 1     |
| Mike Johnson| Housekeeping| 2    |

**Notes:**
- First column: Staff Name
- Second column: Department  
- Third column: Day (1 or 2)
- Supported formats: Excel (.xlsx, .xls) or CSV
- Include headers in first row

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1. **Clone or download the project**
   ```bash
   cd lucky-draw
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\Activate.ps1`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install django pillow qrcode openpyxl pandas
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open browser and go to: `http://127.0.0.1:8000`
   - Login with: `hr_admin` / `staff_party_2024`

## Usage Guide

### 1. Initial Setup
1. Login with HR Admin credentials
2. Upload staff list using "Upload Staff List" feature
3. Download generated QR codes for distribution

### 2. Event Day Operations
1. **Check-ins**: Use "Scan QR Code" on mobile device
2. **Lucky Draw**: Use "Draw Winner" buttons on dashboard
3. **Monitoring**: View check-ins and winners in real-time

### 3. QR Code Scanning
- Access scan page on mobile device
- Allow camera permissions
- Point camera at staff QR codes
- Automatic check-in processing

### 4. Lucky Draw Process
- Click "Draw Winner - Day 1" or "Draw Winner - Day 2"
- Winner appears on screen
- Repeat for up to 5 winners per day
- Only checked-in staff are eligible

## Technical Details

### Models
- **Staff**: Staff information and QR codes
- **CheckIn**: Check-in records with timestamps
- **Winner**: Lucky draw winners with draw order

### Key Features
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: AJAX-based interactions
- **Security**: CSRF protection and input validation
- **File Processing**: Excel/CSV upload with pandas
- **QR Generation**: Automatic QR code creation with qrcode library

### API Endpoints
- `POST /process-qr-scan/`: Process QR code scans
- `POST /draw-winner/`: Execute lucky draw
- `GET /view-checkins/`: View check-in records
- `GET /view-winners/`: View lucky draw winners

## Sample Data

A sample CSV file (`sample_staff_list.csv`) is included for testing the upload functionality.

## Browser Compatibility

- Chrome (recommended for QR scanning)
- Firefox
- Safari
- Edge

**Note**: QR code scanning requires HTTPS in production or localhost for development.

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Use HTTPS for QR code scanning
5. Configure proper security settings

## Support

For issues or questions:
1. Check browser console for JavaScript errors
2. Verify file format matches requirements
3. Ensure camera permissions are granted for QR scanning
4. Check Django logs for server-side errors

---

**Built with Django, Bootstrap, and HTML5 QR Code Scanner** 
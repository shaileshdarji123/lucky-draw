from django.http import HttpResponse, JsonResponse, FileResponse
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
import pandas as pd
import random
import json
from .models import Staff, CheckIn, Winner, EventSettings
from .forms import StaffUploadForm, QRCodeScanForm, EventSettingsForm
from django.utils import timezone
from datetime import date

# SVG preview endpoint for QR code
@login_required
def preview_qr_svg(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    import qrcode
    try:
        from qrcode.image.svg import SvgImage
    except ImportError:
        return HttpResponse("SVG QR code generation requires qrcode >=6.1. Please upgrade the qrcode package.", status=500)
    qr_data = f"{staff.id}:{staff.day_1}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    svg_img = qr.make_image(image_factory=SvgImage)
    svg_bytes = BytesIO()
    svg_img.save(svg_bytes)
    svg_bytes.seek(0)
    label = f"{staff.name} | {staff.department} | Day {staff.day_1}"
    svg_content = svg_bytes.getvalue().decode('utf-8')
    import re
    m = re.search(r'viewBox="(\d+) (\d+) (\d+) (\d+)"', svg_content)
    if m:
        x, y, w, h = map(int, m.groups())
        label_y = h + 30
        label_x = w // 2
        label_svg = f'<text x="{label_x}" y="{label_y}" text-anchor="middle" font-size="22" fill="#222">{label}</text>'
        svg_content = svg_content.replace('</svg>', label_svg + '</svg>')
    return HttpResponse(svg_content, content_type='image/svg+xml')

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"



@login_required
def download_qr_with_label(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    import qrcode
    from io import BytesIO
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return HttpResponse("JPG QR code generation requires Pillow. Please install pillow.", status=500)
    # Generate QR code as PIL image (lightweight)
    qr_data = f"{staff.id}:{staff.day_1}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    width, height = qr_img.size
    label = f"{staff.name} | {staff.department} | Day {staff.day_1}"
    # Use default font for max compatibility
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(qr_img)
    # Calculate label size (Pillow compatibility)
    try:
        bbox = draw.textbbox((0, 0), label, font=font)
        label_width = bbox[2] - bbox[0]
        label_height = bbox[3] - bbox[1]
    except AttributeError:
        label_width, label_height = draw.textsize(label, font=font)
    # Create new image with space for label
    new_height = height + label_height + 10
    new_img = Image.new('RGB', (width, new_height), 'white')
    new_img.paste(qr_img, (0, 0))
    # Draw label centered below QR
    text_x = (width - label_width) // 2
    text_y = height + 5
    draw_label = ImageDraw.Draw(new_img)
    draw_label.text((text_x, text_y), label, font=font, fill=(30,30,30))
    # Save as lightweight JPG
    buffer = BytesIO()
    new_img.save(buffer, format='JPEG', quality=80, optimize=True)
    buffer.seek(0)
    filename = f"{staff.name.replace(' ', '-').lower()}_{staff.department.replace(' ', '-').lower()}_{staff.day_1}.jpg"
    response = HttpResponse(buffer.getvalue(), content_type='image/jpeg')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
import pandas as pd
import random
import json

from .models import Staff, CheckIn, Winner, EventSettings
from .forms import StaffUploadForm, QRCodeScanForm, EventSettingsForm
from django.utils import timezone
from datetime import date

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Fixed credentials for HR Admin
        if username == 'hr_admin' and password == 'staff_party_2024':
            user = authenticate(request, username=username, password=password)
            if user is None:
                # Create a dummy user for authentication
                from django.contrib.auth.models import User
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'is_staff': True, 'is_superuser': True}
                )
                if created:
                    user.set_password(password)
                    user.save()
            
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials. Use hr_admin / staff_party_2024')
    
    return render(request, 'lucky_draw/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def require_event_dates(view_func):
    def _wrapped_view(request, *args, **kwargs):
        settings = EventSettings.get_solo()
        if not settings.day1_date or not settings.day2_date:
            return redirect('set_event_dates')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def set_event_dates(request):
    settings = EventSettings.get_solo()
    if request.method == 'POST':
        form = EventSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event dates updated successfully.')
            return redirect('dashboard')
    else:
        form = EventSettingsForm(instance=settings)
    return render(request, 'lucky_draw/set_event_dates.html', {'form': form})

@login_required
def dashboard(request):
    settings = EventSettings.get_solo()
    if not settings.day1_date or not settings.day2_date:
        return redirect('set_event_dates')
    day1_checkins_count = CheckIn.objects.filter(day=1).count()
    day2_checkins_count = CheckIn.objects.filter(day=2).count()
    clear_db_env = os.getenv('CLEAR_DB_ENABLED', 'True').strip().lower()
    clear_db_enabled = clear_db_env in ['true', '1', 'yes', 'on']
    context = {
        'total_staff': Staff.objects.count(),
        'day1_checkins': day1_checkins_count,
        'day2_checkins': day2_checkins_count,
        'day1_winners': Winner.objects.filter(day=1).count(),
        'day2_winners': Winner.objects.filter(day=2).count(),
        'event_settings': settings,
        'can_draw_day1': day1_checkins_count >= 5,
        'can_draw_day2': day2_checkins_count >= 5,
        'draw_msg_day1': '' if day1_checkins_count >= 5 else 'At least 5 staff must be checked in for Day 1 to enable the draw.',
        'draw_msg_day2': '' if day2_checkins_count >= 5 else 'At least 5 staff must be checked in for Day 2 to enable the draw.',
        'clear_db_enabled': clear_db_enabled,
    }
    return render(request, 'lucky_draw/dashboard.html', context)

@login_required
def upload_staff(request):
    if request.method == 'POST':
        form = StaffUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES['file']
                
                # Read the file based on extension
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Clear existing staff
                Staff.objects.all().delete()
                
                # Process each row
                for index, row in df.iterrows():
                    staff_name = row.iloc[0]  # First column
                    department = row.iloc[1]  # Second column
                    day = int(row.iloc[2])    # Third column
                    
                    Staff.objects.create(
                        name=staff_name,
                        department=department,
                        day_1=day
                    )
                
                messages.success(request, f'Successfully uploaded {len(df)} staff members')
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = StaffUploadForm()
    
    return render(request, 'lucky_draw/upload_staff.html', {'form': form})

@login_required
@require_event_dates
def scan_qr(request):
    return render(request, 'lucky_draw/scan_qr.html')

@login_required
@csrf_exempt
@require_http_methods(["POST"])
@require_event_dates
def process_qr_scan(request):
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data')
        
        if not qr_data:
            return JsonResponse({'success': False, 'message': 'No QR data provided'})
        
        staff_id, day = qr_data.split(':')
        staff = get_object_or_404(Staff, id=int(staff_id))
        day = int(day)
        settings = EventSettings.get_solo()
        today = date.today()
        # Validation: Only allow check-in for the correct day
        if day == 1 and today != settings.day1_date:
            return JsonResponse({'success': False, 'message': f'Check-in for Day 1 is only allowed on {settings.day1_date}.'})
        if day == 2 and today != settings.day2_date:
            return JsonResponse({'success': False, 'message': f'Check-in for Day 2 is only allowed on {settings.day2_date}.'})
        
        # Check if already checked in
        if CheckIn.objects.filter(staff=staff, day=day).exists():
            return JsonResponse({
                'success': False, 
                'message': f'{staff.name} has already been checked in for Day {day}'
            })
        
        # Create check-in
        CheckIn.objects.create(staff=staff, day=day)
        
        return JsonResponse({
            'success': True,
            'message': f'{staff.name} from {staff.department} successfully checked in for Day {day}',
            'staff_name': staff.name,
            'department': staff.department,
            'day': day
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def draw_winner(request):
    try:
        data = json.loads(request.body)
        day = int(data.get('day'))
        if day not in [1, 2]:
            return JsonResponse({'success': False, 'message': 'Invalid day'})
        checked_in_staff = list(CheckIn.objects.filter(day=day).values_list('staff_id', flat=True))
        existing_winners = list(Winner.objects.filter(day=day).values_list('staff_id', flat=True))
        # Enforce maximum of 5 winners per day
        if len(existing_winners) >= 5:
            return JsonResponse({'success': False, 'message': f'Maximum of 5 winners already drawn for Day {day}.'})
        if len(checked_in_staff) < 5:
            return JsonResponse({'success': False, 'message': f'At least 5 staff must be checked in for Day {day} to draw winners.'})
        available_staff = list(set(checked_in_staff) - set(existing_winners))
        if not available_staff:
            return JsonResponse({
                'success': False, 
                'message': f'No more available staff for Day {day} lucky draw'
            })
        # Use a lottery algorithm: shuffle and pick one
        import random
        random.shuffle(available_staff)
        winner_staff_id = available_staff[0]
        winner_staff = Staff.objects.get(id=winner_staff_id)
        next_order = Winner.objects.filter(day=day).count() + 1
        winner = Winner.objects.create(
            staff=winner_staff,
            day=day,
            draw_order=next_order
        )
        return JsonResponse({
            'success': True,
            'message': f'Winner #{next_order} for Day {day}: {winner_staff.name} from {winner_staff.department}',
            'winner_name': winner_staff.name,
            'department': winner_staff.department,
            'draw_order': next_order
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

@login_required
def view_checkins(request):
    day1_checkins = CheckIn.objects.filter(day=1).select_related('staff').order_by('-checked_in_at')
    day2_checkins = CheckIn.objects.filter(day=2).select_related('staff').order_by('-checked_in_at')
    
    context = {
        'day1_checkins': day1_checkins,
        'day2_checkins': day2_checkins,
    }
    return render(request, 'lucky_draw/view_checkins.html', context)

@login_required
def view_winners(request):
    day1_winners = Winner.objects.filter(day=1).select_related('staff').order_by('draw_order')
    day2_winners = Winner.objects.filter(day=2).select_related('staff').order_by('draw_order')
    
    context = {
        'day1_winners': day1_winners,
        'day2_winners': day2_winners,
    }
    return render(request, 'lucky_draw/view_winners.html', context)

@login_required
def download_qr_codes(request):
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    staff_list = Staff.objects.all().order_by('name')
    departments = Staff.objects.values_list('department', flat=True).distinct()
    days = [1, 2]
    department_filter = request.GET.get('department', '')
    day_filter = request.GET.get('day', '')
    checked_in_filter = request.GET.get('checked_in', '')
    search_query = request.GET.get('search', '').strip()
    # Annotate staff with check-in status
    from django.db.models import Exists, OuterRef, Q
    staff_list = staff_list.annotate(
        checked_in=Exists(CheckIn.objects.filter(staff=OuterRef('pk'), day=OuterRef('day_1')))
    )
    if department_filter:
        staff_list = staff_list.filter(department=department_filter)
    if day_filter:
        staff_list = staff_list.filter(day_1=day_filter)
    if checked_in_filter == 'hide':
        staff_list = staff_list.filter(checked_in=False)
    # Search: prioritize name, then department, then day
    if search_query:
        staff_list = staff_list.filter(
            Q(name__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(day_1__icontains=search_query)
        ).order_by(
            # Custom ordering: name matches first, then department, then day
            '-name', '-department', '-day_1'
        )
    # Pagination - use dynamic items per page based on viewport
    page = request.GET.get('page', 1)
    
    # Get the per_page parameter from the request, with fallback to default
    try:
        per_page = int(request.GET.get('per_page', 12))
        # Constrain per_page to reasonable values to prevent abuse
        per_page = max(4, min(per_page, 48))  # Between 4 and 48 items
    except (ValueError, TypeError):
        # Default if not a valid number
        per_page = 12
    
    # Create paginator with dynamic page size
    paginator = Paginator(staff_list, per_page)
    
    try:
        staff_page = paginator.page(page)
    except PageNotAnInteger:
        staff_page = paginator.page(1)
    except EmptyPage:
        staff_page = paginator.page(paginator.num_pages)
    # Prepare staff list for JSON
    def staff_to_dict(staff):
        return {
            'id': staff.id,
            'name': staff.name,
            'department': staff.department,
            'day_1': staff.day_1,
            'checked_in': staff.checked_in,
        }
    staff_objs = list(staff_page.object_list) if staff_page else []
    staff_list_json = json.dumps([staff_to_dict(s) for s in staff_objs])
    if request.GET.get('ajax') == '1':
        return JsonResponse({
            'staff_list': [staff_to_dict(s) for s in staff_page.object_list],
            'page': staff_page.number,
            'num_pages': paginator.num_pages,
            'per_page': per_page,
            'total_count': paginator.count
        })
    return render(request, 'lucky_draw/download_qr_codes.html', {
        'staff_list': staff_page,
        'staff_list_json': staff_list_json,
        'departments': departments,
        'days': days,
        'department_filter': department_filter,
        'day_filter': day_filter,
        'checked_in_filter': checked_in_filter,
        'search_query': search_query,
        'paginator': paginator,
        'page_obj': staff_page,
    })

@require_POST
@login_required
def delete_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        staff.delete()
        return JsonResponse({'success': True})
    except Staff.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Staff not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def clear_database(request):
    clear_db_env = os.getenv('CLEAR_DB_ENABLED', 'True').strip().lower()
    clear_db_enabled = clear_db_env in ['true', '1', 'yes', 'on']
    if request.method == 'POST':
        if not clear_db_enabled:
            messages.error(request, 'Database clearing is disabled by admin.')
            return redirect('dashboard')
        Staff.objects.all().delete()
        CheckIn.objects.all().delete()
        Winner.objects.all().delete()
        EventSettings.objects.all().delete()
        messages.success(request, 'Database cleared!')
        return redirect('dashboard')
    return render(request, 'lucky_draw/clear_db_confirm.html', {'clear_db_enabled': clear_db_enabled})

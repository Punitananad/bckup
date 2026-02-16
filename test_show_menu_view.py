#!/usr/bin/env python
"""
Test the show_menu view to see what's causing the 404
"""
import os
import sys
import django
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'application', 'scan2food'))
django.setup()

from django.test import RequestFactory
from theatre.views import show_menu
from theatre.models import Seat

def test_show_menu(seat_id):
    """Test the show_menu view with detailed error reporting"""
    print(f"\n{'='*60}")
    print(f"Testing show_menu view for Seat ID: {seat_id}")
    print(f"{'='*60}\n")
    
    try:
        # First verify seat exists
        seat = Seat.objects.get(pk=seat_id)
        print(f"✓ Seat found: {seat.name}")
        print(f"  - Row: {seat.row.name}")
        print(f"  - Hall: {seat.row.hall.name}")
        print(f"  - Theatre: {seat.row.hall.theatre.name}")
        print(f"  - Is Vacant: {seat.is_vacent}")
        
        # Check theatre details
        theatre = seat.row.hall.theatre
        print(f"\n✓ Theatre details:")
        print(f"  - Name: {theatre.name}")
        print(f"  - Service End Time: {theatre.service_end_time}")
        
        # Check if theatre.detail exists
        try:
            detail = theatre.detail
            print(f"  - Scanning Service: {detail.scaning_service}")
            print(f"  - Is Active: {detail.is_active}")
        except Exception as e:
            print(f"  ✗ Theatre detail error: {e}")
        
        # Now test the actual view
        print(f"\n{'='*60}")
        print(f"Testing actual view function...")
        print(f"{'='*60}\n")
        
        factory = RequestFactory()
        request = factory.get(f'/theatre/show-menu/{seat_id}/')
        
        # Add required attributes to request
        request.user = type('User', (), {'is_authenticated': False})()
        
        response = show_menu(request, seat_id)
        
        print(f"✓ View executed successfully!")
        print(f"  - Status Code: {response.status_code}")
        print(f"  - Content Type: {response.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print(f"\n✓ SUCCESS! The view works correctly.")
        else:
            print(f"\n⚠ View returned status {response.status_code}")
            
    except Seat.DoesNotExist:
        print(f"✗ Seat {seat_id} does not exist!")
        
    except Exception as e:
        print(f"\n✗ ERROR occurred:")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Error Message: {str(e)}")
        print(f"\nFull Traceback:")
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_show_menu_view.py <seat_id>")
        print("Example: python test_show_menu_view.py 2442")
        sys.exit(1)
    
    seat_id = int(sys.argv[1])
    test_show_menu(seat_id)

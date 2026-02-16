#!/usr/bin/env python
"""
Check if a specific seat exists in the database
Usage: python check_seat_exists.py <seat_id>
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'application', 'scan2food'))
django.setup()

from theatre.models import Seat, Row, Hall, Theatre

def check_seat(seat_id):
    """Check if a seat exists and show its details"""
    print(f"\n{'='*60}")
    print(f"Checking Seat ID: {seat_id}")
    print(f"{'='*60}\n")
    
    try:
        seat = Seat.objects.get(pk=seat_id)
        print(f"✓ Seat FOUND!")
        print(f"  - Seat Name: {seat.name}")
        print(f"  - Row: {seat.row.name}")
        print(f"  - Hall: {seat.row.hall.name}")
        print(f"  - Theatre: {seat.row.hall.theatre.name}")
        print(f"  - Is Vacant: {seat.is_vacent}")
        return True
        
    except Seat.DoesNotExist:
        print(f"✗ Seat NOT FOUND!")
        print(f"\nSearching for similar seats...")
        
        # Show nearby seat IDs
        nearby_seats = Seat.objects.filter(
            pk__gte=seat_id-10, 
            pk__lte=seat_id+10
        ).values_list('pk', 'name', 'row__name', 'row__hall__name')
        
        if nearby_seats:
            print(f"\nNearby seats (±10 IDs):")
            for pk, name, row, hall in nearby_seats:
                print(f"  - Seat ID {pk}: {name} (Row: {row}, Hall: {hall})")
        else:
            print(f"  No seats found near ID {seat_id}")
        
        # Show all seats
        total_seats = Seat.objects.count()
        print(f"\nTotal seats in database: {total_seats}")
        
        if total_seats > 0:
            first_seat = Seat.objects.first()
            last_seat = Seat.objects.last()
            print(f"Seat ID range: {first_seat.pk} to {last_seat.pk}")
            
            # Show first 10 seats
            print(f"\nFirst 10 seats:")
            for seat in Seat.objects.all()[:10]:
                print(f"  - Seat ID {seat.pk}: {seat.name} (Row: {seat.row.name}, Hall: {seat.row.hall.name})")
        
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_seat_exists.py <seat_id>")
        print("Example: python check_seat_exists.py 2442")
        sys.exit(1)
    
    seat_id = int(sys.argv[1])
    check_seat(seat_id)

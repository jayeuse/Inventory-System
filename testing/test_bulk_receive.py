"""
Test script for Bulk Receive functionality
This demonstrates Layer 1 (Row Locking) and Layer 3 (Bulk Receive Endpoint)
"""

import requests
import json

# Base URL - adjust if your server runs on different port
BASE_URL = "http://localhost:8000/api"

def test_bulk_receive():
    """
    Test the bulk receive endpoint
    
    Prerequisites:
    1. Server must be running (python manage.py runserver)
    2. Sample data must be inserted (python manage.py insert_sample_data)
    3. You need valid order and order_item IDs from the database
    """
    
    # Example bulk receive request
    bulk_receive_data = {
        "items": [
            {
                "order": "ORD-2025-00001",  # Replace with actual order ID
                "order_item": "ITM-00001",   # Replace with actual order item ID
                "quantity_received": 50,
                "received_by": "John Doe - Test",
                "expiry_date": "2026-12-31"  # Optional
            },
            {
                "order": "ORD-2025-00001",
                "order_item": "ITM-00002",
                "quantity_received": 30,
                "received_by": "John Doe - Test",
                "expiry_date": "2026-11-30"
            }
        ]
    }
    
    print("=" * 80)
    print("TESTING BULK RECEIVE ENDPOINT")
    print("=" * 80)
    print("\nRequest Data:")
    print(json.dumps(bulk_receive_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/receive-orders/bulk_receive/",
            json=bulk_receive_data,
            headers={"Content-Type": "application/json"}
        )
        
        print("\n" + "=" * 80)
        print(f"Response Status: {response.status_code}")
        print("=" * 80)
        print("\nResponse Data:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 201:
            print("\n✅ SUCCESS: Bulk receive completed successfully!")
        else:
            print("\n❌ FAILED: Bulk receive encountered errors")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server. Is it running?")
        print("Start server with: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_concurrent_receive_protection():
    """
    Test that row locking prevents over-receiving in concurrent scenarios
    
    This would require simulating concurrent requests, which is complex.
    In practice, you'd use threading or multiprocessing to test this.
    """
    print("\n" + "=" * 80)
    print("TESTING ROW LOCKING (Concurrent Protection)")
    print("=" * 80)
    print("\nThis requires manual testing with concurrent requests.")
    print("\nTo test:")
    print("1. Find an order item with remaining quantity")
    print("2. Open two browser tabs or API clients")
    print("3. Try to receive MORE than remaining in BOTH simultaneously")
    print("4. Only ONE should succeed due to row locking")
    print("\nExample scenario:")
    print("  - Ordered: 100 units")
    print("  - Already received: 80 units")
    print("  - Remaining: 20 units")
    print("  - Try to receive 30 units in Tab A")
    print("  - Try to receive 30 units in Tab B (at same time)")
    print("  - Expected: BOTH should fail with friendly error message")
    print("  - Without locking: One might succeed (WRONG!)")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("BULK RECEIVE & ROW LOCKING TEST SUITE")
    print("=" * 80)
    
    print("\n⚠️  IMPORTANT: Update the order and order_item IDs in the script")
    print("              with actual IDs from your database!\n")
    
    choice = input("Run bulk receive test? (y/n): ").lower()
    if choice == 'y':
        test_bulk_receive()
    
    print("\n")
    test_concurrent_receive_protection()
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)

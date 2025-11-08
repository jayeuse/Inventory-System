"""
Test concurrent receive protection with threading
"""
import threading
import time
import json

def simulate_receive(thread_name, order_item, quantity):
    """Simulate a receive order request"""
    import urllib.request
    
    url = "http://localhost:8000/api/receive-orders/"
    data = {
        "order": "ORD-2025-00005",
        "order_item": order_item,
        "quantity_received": quantity,
        "received_by": f"Thread {thread_name}"
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"[{thread_name}] Sending request...")
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        print(f"[{thread_name}] ✅ SUCCESS: {result.get('receive_order_id')}")
        return True
        
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode('utf-8'))
        print(f"[{thread_name}] ❌ FAILED: {error_data}")
        return False
    except Exception as e:
        print(f"[{thread_name}] ❌ ERROR: {str(e)}")
        return False


def test_concurrent_receive():
    """Test that only one of two concurrent requests succeeds"""
    print("="*80)
    print("TESTING CONCURRENT RECEIVE PROTECTION")
    print("="*80)
    print("\nScenario: ITM-00012 (Similac)")
    print("  Ordered: 100")
    print("  Already Received: 50")
    print("  Remaining: 50")
    print("\nTest: Two threads both try to receive 40 units simultaneously")
    print("Expected: Only ONE should succeed due to row locking\n")
    
    # Create two threads that will run simultaneously
    thread1 = threading.Thread(
        target=simulate_receive,
        args=("Thread-1", "ITM-00012", 40)
    )
    thread2 = threading.Thread(
        target=simulate_receive,
        args=("Thread-2", "ITM-00012", 40)
    )
    
    # Start both threads at nearly the same time
    thread1.start()
    thread2.start()
    
    # Wait for both to complete
    thread1.join()
    thread2.join()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nIf row locking works correctly:")
    print("  - One thread should show ✅ SUCCESS")
    print("  - Other thread should show ❌ FAILED with validation error")
    print("  - If BOTH succeed, row locking is NOT working! ⚠️")


if __name__ == "__main__":
    print("\n⚠️  Make sure server is running: python manage.py runserver\n")
    input("Press Enter to start test...")
    test_concurrent_receive()

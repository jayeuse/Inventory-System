# Bulk Receive & Row Locking Implementation

## ✅ Implementation Complete

### Layer 1: Row Locking (Concurrency Protection)
### Layer 3: Bulk Receive Endpoint

---

## 🔒 Layer 1: Row Locking

### What It Does
Prevents race conditions when multiple users try to receive the same order item simultaneously.

### How It Works
```python
# In ReceiveOrderSerializer.validate()
with transaction.atomic():
    # Lock the order_item row - no one else can modify it until we're done
    locked_order_item = OrderItem.objects.select_for_update().get(pk=order_item.pk)
    
    # Calculate totals with lock held
    # Validate quantity
    # Save receive order
    # Lock is released automatically
```

### Example Scenario
**Without Row Locking (PROBLEM):**
- Order: 100 units
- User A receives 80 units → Check: 0 received, OK ✅
- User B receives 80 units → Check: 0 received, OK ✅  
- Result: 160 units recorded! ❌

**With Row Locking (SOLUTION):**
- Order: 100 units
- User A starts receiving 80 units → LOCKS order item
- User B tries to receive 80 units → WAITS for lock
- User A completes → 80 units recorded → UNLOCKS
- User B now checks → 80 already received → REJECTS with error ✅

---

## 🚀 Layer 3: Bulk Receive Endpoint

### Endpoint
```
POST /api/receive-orders/bulk_receive/
```

### Request Body
```json
{
  "items": [
    {
      "order": "ORD-2025-00001",
      "order_item": "ITM-00001",
      "quantity_received": 100,
      "received_by": "John Doe",
      "expiry_date": "2026-12-31"
    },
    {
      "order": "ORD-2025-00001",
      "order_item": "ITM-00002",
      "quantity_received": 50,
      "received_by": "John Doe"
    }
  ]
}
```

### Response (Success)
```json
{
  "message": "Successfully received 2 item(s)",
  "results": [
    {
      "index": 0,
      "receive_order_id": "RCV-00001",
      "order_item_id": "ITM-00001",
      "product_name": "Amoxil Amoxicillin 500mg",
      "quantity_received": 100,
      "status": "success"
    },
    {
      "index": 1,
      "receive_order_id": "RCV-00002",
      "order_item_id": "ITM-00002",
      "product_name": "Tylenol Paracetamol 500mg",
      "quantity_received": 50,
      "status": "success"
    }
  ],
  "total_items": 2,
  "successful": 2,
  "failed": 0
}
```

### Response (Validation Error)
```json
{
  "message": "Bulk receive failed. All items rolled back.",
  "errors": [
    {
      "index": 0,
      "order_item": "ITM-00001",
      "error": {
        "quantity_received": "Cannot receive 150 units. Ordered: 100, Already received: 0, Remaining: 100"
      }
    }
  ],
  "successful_items": []
}
```

### Features
- ✅ **All-or-Nothing**: If ANY item fails validation, NOTHING is saved
- ✅ **Row Locking**: Locks all order items upfront to prevent race conditions
- ✅ **Atomic Transaction**: All receives happen in one database transaction
- ✅ **Detailed Errors**: Shows exactly what went wrong for each item
- ✅ **Better Performance**: One API call instead of multiple

---

## 📊 Benefits

### 1. Data Integrity
- **Prevents over-receiving** - impossible to receive more than ordered
- **No race conditions** - concurrent users can't corrupt data
- **Atomic operations** - all items succeed or all fail

### 2. Better User Experience
- **Friendly error messages** - tells you exactly what's wrong
- **Shows remaining quantity** - helps users know how much they CAN receive
- **Bulk operations** - receive entire shipment in one click

### 3. Performance
- **Fewer API calls** - 1 bulk call instead of N individual calls
- **Better locking** - locks all items upfront, not one-by-one
- **Reduced network overhead** - less HTTP round trips

---

## 🧪 Testing

### Test Row Locking
1. Find an order item with remaining quantity
2. Open two API clients (Postman, browser tabs, etc.)
3. Try to receive MORE than remaining in BOTH simultaneously
4. Expected: Both should fail with helpful error message

### Test Bulk Receive
1. Start server: `python manage.py runserver`
2. Use test script: `python testing/test_bulk_receive.py`
3. Or use Postman/curl with the endpoint

### Example with curl
```bash
curl -X POST http://localhost:8000/api/receive-orders/bulk_receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "order": "ORD-2025-00001",
        "order_item": "ITM-00001",
        "quantity_received": 50,
        "received_by": "Test User",
        "expiry_date": "2026-12-31"
      }
    ]
  }'
```

---

## 🎯 Use Cases

### Use Case 1: Receiving Partial Shipment
```
Scenario: Shipment arrives with 3 products
- Amoxil: 100 units
- Tylenol: 50 units  
- Centrum: 75 units

Solution: Use bulk_receive to record all 3 in one transaction
```

### Use Case 2: Preventing Warehouse Staff Conflicts
```
Scenario: Two staff members both try to receive the same item
- Staff A: Tries to receive 80 units
- Staff B: Tries to receive 80 units (simultaneously)
- Only 100 ordered

Solution: Row locking ensures only one succeeds, the other gets clear error
```

### Use Case 3: Mobile App Offline Sync
```
Scenario: Warehouse staff records receives on mobile, syncs later
- Multiple receives queued up offline
- Need to sync all at once when online

Solution: Bulk receive uploads all items in one atomic transaction
```

---

## ⚠️ Important Notes

### Transaction Isolation
- Row locking uses `SELECT FOR UPDATE`
- Blocks concurrent modifications to same order item
- Locks are released automatically when transaction completes

### Validation Order
1. Check all order items exist
2. Lock all order items
3. Validate each receive quantity
4. If ANY fail → rollback ALL
5. If ALL pass → commit ALL

### Error Handling
- Individual item errors collected, not thrown immediately
- All items validated before any are saved
- If errors exist, entire transaction rolls back
- User gets detailed error report

---

## 🔄 Future Enhancements (Optional)

### Layer 2: Database Constraint
For absolute guarantee, add PostgreSQL trigger:
```sql
CREATE TRIGGER receive_order_quantity_check
  BEFORE INSERT OR UPDATE ON receive_order
  FOR EACH ROW
  EXECUTE FUNCTION check_receive_order_quantity();
```

### Partial Success Option
Allow some items to succeed even if others fail:
```json
{
  "partial_success_allowed": true,
  "items": [...]
}
```

### Batch Status Reporting
Return order status after bulk receive:
```json
{
  "order_status_updated": [
    {
      "order_id": "ORD-2025-00001",
      "old_status": "Pending",
      "new_status": "Partially Received"
    }
  ]
}
```

---

## 📚 Related Documentation

- Django `select_for_update()`: https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-for-update
- DRF Custom Actions: https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
- Database Transactions: https://docs.djangoproject.com/en/stable/topics/db/transactions/

---

**Implementation Status:** ✅ Complete and Ready for Testing

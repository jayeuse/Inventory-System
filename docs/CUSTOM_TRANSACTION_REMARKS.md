# Custom Transaction Remarks & Performed By

## Overview

You can now provide custom `remarks` and `performed_by` values when creating transactions through:
1. **ReceiveOrder** (Stock IN transactions)
2. **ProductBatch** manual adjustments (ADJ transactions)

If not provided, the system will use sensible defaults.

---

## 📦 ReceiveOrder - Custom Transaction Details

### API Endpoint
`POST /api/receive-orders/`
`PUT /api/receive-orders/{receive_order_id}/`

### Request Body

```json
{
  "order": "ORD-2025-00001",
  "order_item": "ITM-00001",
  "quantity_received": 100,
  "received_by": "John Doe",
  "expiry_date": "2026-12-31",
  
  // Optional custom transaction fields
  "transaction_remarks": "Urgent delivery - stored in refrigerated section",
  "transaction_performed_by": "Sarah Johnson, Head Pharmacist"
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction_remarks` | string | No | Custom remarks for the stock-in transaction |
| `transaction_performed_by` | string | No | Who performed this transaction (overrides `received_by`) |

### Default Behavior (if not provided)

- **`performed_by`**: Uses `received_by` field value
- **`remarks`**: Auto-generated as: `"Received {quantity} units from {supplier} via Order {order_id}"`

### Example with Defaults

**Request:**
```json
{
  "order": "ORD-2025-00001",
  "order_item": "ITM-00001",
  "quantity_received": 100,
  "received_by": "John Doe"
}
```

**Transaction Created:**
```json
{
  "transaction_type": "IN",
  "quantity_change": "+100",
  "performed_by": "John Doe",
  "remarks": "Received 100 units from PharmaCare Distributors Inc. via Order ORD-2025-00001"
}
```

### Example with Custom Fields

**Request:**
```json
{
  "order": "ORD-2025-00001",
  "order_item": "ITM-00001",
  "quantity_received": 100,
  "received_by": "John Doe",
  "transaction_remarks": "Emergency stock - Priority delivery from supplier",
  "transaction_performed_by": "Sarah Johnson, Head Pharmacist"
}
```

**Transaction Created:**
```json
{
  "transaction_type": "IN",
  "quantity_change": "+100",
  "performed_by": "Sarah Johnson, Head Pharmacist",
  "remarks": "Emergency stock - Priority delivery from supplier"
}
```

---

## 🔧 ProductBatch - Custom Adjustment Details

### API Endpoint
`PUT /api/product-batches/{batch_id}/`
`PATCH /api/product-batches/{batch_id}/`

### Request Body

```json
{
  "on_hand": 75,
  
  // Optional custom transaction fields
  "transaction_remarks": "5 units damaged during inventory check - discarded",
  "transaction_performed_by": "Mike Davis, Inventory Manager"
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transaction_remarks` | string | No | Custom remarks for the adjustment transaction |
| `transaction_performed_by` | string | No | Who performed this adjustment |

### Default Behavior (if not provided)

- **`performed_by`**: `"Manual Adjustment"`
- **`remarks`**: Auto-generated as: `"Manual adjustment to batch {batch_id}: {old_qty} → {new_qty}"`

### Example with Defaults

**Request:**
```json
{
  "on_hand": 75
}
```

**Before:** `on_hand = 100`

**Transaction Created:**
```json
{
  "transaction_type": "ADJ",
  "quantity_change": "-25",
  "performed_by": "Manual Adjustment",
  "remarks": "Manual adjustment to batch PRD-00001-BAT-00001: 100 → 75"
}
```

### Example with Custom Fields

**Request:**
```json
{
  "on_hand": 75,
  "transaction_remarks": "Inventory discrepancy found during audit - 25 units unaccounted for",
  "transaction_performed_by": "Emily Chen, Auditor"
}
```

**Transaction Created:**
```json
{
  "transaction_type": "ADJ",
  "quantity_change": "-25",
  "performed_by": "Emily Chen, Auditor",
  "remarks": "Inventory discrepancy found during audit - 25 units unaccounted for"
}
```

---

## 💡 Use Cases

### Receiving Orders with Context

```json
{
  "order_item": "ITM-00001",
  "quantity_received": 500,
  "received_by": "John Doe",
  "transaction_remarks": "Partial delivery - remaining 200 units expected next week",
  "transaction_performed_by": "John Doe, Receiving Clerk"
}
```

### Adjustments with Reasons

**Damaged Goods:**
```json
{
  "on_hand": 95,
  "transaction_remarks": "5 units damaged - broken packaging found during inspection",
  "transaction_performed_by": "QA Team"
}
```

**Inventory Count Corrections:**
```json
{
  "on_hand": 148,
  "transaction_remarks": "Physical count correction - system showed 150, actual 148",
  "transaction_performed_by": "Annual Inventory Audit Team"
}
```

**Expired Items Disposal:**
```json
{
  "on_hand": 0,
  "transaction_remarks": "Batch expired on 2025-10-15 - disposed per pharmacy protocols",
  "transaction_performed_by": "Disposal Unit"
}
```

---

## 🧪 Testing

### Test Custom Remarks on ReceiveOrder

```bash
# Create a receive order with custom transaction details
curl -X POST http://127.0.0.1:8000/api/receive-orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "order": "ORD-2025-00001",
    "order_item": "ITM-00001",
    "quantity_received": 100,
    "received_by": "Test User",
    "transaction_remarks": "Test custom remarks",
    "transaction_performed_by": "Test Performer"
  }'

# Check the transaction
curl http://127.0.0.1:8000/api/transactions/
```

### Test Custom Remarks on Batch Adjustment

```bash
# Adjust batch quantity with custom details
curl -X PATCH http://127.0.0.1:8000/api/product-batches/PRD-00001-BAT-00001/ \
  -H "Content-Type: application/json" \
  -d '{
    "on_hand": 75,
    "transaction_remarks": "Testing adjustment with custom notes",
    "transaction_performed_by": "Test Adjuster"
  }'

# Check the transaction
curl http://127.0.0.1:8000/api/transactions/
```

---

## ✅ Summary

| Operation | Default `performed_by` | Default `remarks` |
|-----------|----------------------|-------------------|
| **ReceiveOrder** | `received_by` field | "Received X units from {supplier} via Order {order_id}" |
| **Batch Adjustment** | "Manual Adjustment" | "Manual adjustment to batch {batch_id}: {old} → {new}" |

**Custom fields are optional** - the system will always work with sensible defaults if you don't provide them.

-- Fix Database Schema
-- Run this SQL script to add missing tables and columns

-- 1. Create subcategory table if it doesn't exist
CREATE TABLE IF NOT EXISTS subcategory (
    subcategory_code UUID PRIMARY KEY,
    subcategory_id VARCHAR(15) UNIQUE NOT NULL,
    subcategory_name VARCHAR(100) UNIQUE NOT NULL,
    subcategory_description TEXT,
    category_id VARCHAR(15) NOT NULL REFERENCES category(category_id) ON DELETE CASCADE
);

-- 2. Add missing columns to product table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='product' AND column_name='brand_name') THEN
        ALTER TABLE product ADD COLUMN brand_name VARCHAR(255) NOT NULL DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='product' AND column_name='generic_name') THEN
        ALTER TABLE product ADD COLUMN generic_name VARCHAR(255) NOT NULL DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='product' AND column_name='subcategory_id') THEN
        ALTER TABLE product ADD COLUMN subcategory_id VARCHAR(15) REFERENCES subcategory(subcategory_id) ON DELETE CASCADE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='product' AND column_name='unit_of_measurement') THEN
        ALTER TABLE product ADD COLUMN unit_of_measurement VARCHAR(50);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='product' AND column_name='expiry_threshold_days') THEN
        ALTER TABLE product ADD COLUMN expiry_threshold_days INTEGER DEFAULT 30;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='product' AND column_name='low_stock_threshold') THEN
        ALTER TABLE product ADD COLUMN low_stock_threshold INTEGER DEFAULT 10;
    END IF;
END $$;

-- 3. Create product_stocks table if it doesn't exist
CREATE TABLE IF NOT EXISTS product_stocks (
    stock_code UUID PRIMARY KEY,
    stock_id VARCHAR(30) UNIQUE NOT NULL,
    product_id VARCHAR(20) NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    total_on_hand INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Normal'
);

-- 4. Fix product_batch table - add stock_id if missing
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='product_batch' AND column_name='stock_id') THEN
        ALTER TABLE product_batch ADD COLUMN stock_id VARCHAR(30) REFERENCES product_stocks(stock_id) ON DELETE CASCADE;
    END IF;
END $$;

-- 5. Remove quantity_received, price_per_unit, total_cost from order_item if they exist
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='order_item' AND column_name='quantity_received') THEN
        ALTER TABLE order_item DROP COLUMN quantity_received;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='order_item' AND column_name='price_per_unit') THEN
        ALTER TABLE order_item DROP COLUMN price_per_unit;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='order_item' AND column_name='total_cost') THEN
        ALTER TABLE order_item DROP COLUMN total_cost;
    END IF;
END $$;

-- 6. Create receive_order table
CREATE TABLE IF NOT EXISTS receive_order (
    receive_order_code UUID PRIMARY KEY,
    receive_order_id VARCHAR(30) UNIQUE NOT NULL,
    order_id VARCHAR(20) NOT NULL REFERENCES "order"(order_id) ON DELETE CASCADE,
    order_item_id VARCHAR(30) NOT NULL REFERENCES order_item(order_item_id) ON DELETE CASCADE,
    quantity_received INTEGER NOT NULL,
    date_received TIMESTAMP WITH TIME ZONE NOT NULL,
    received_by TEXT NOT NULL
);

-- 7. Add status to product_stocks if missing (already handled in CREATE TABLE above)

COMMIT;

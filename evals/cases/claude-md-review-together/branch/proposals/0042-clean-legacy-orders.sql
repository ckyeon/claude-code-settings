-- 0042: 오래된 주문 정리
DELETE FROM orders WHERE created_at < '2024-01-01';
ALTER TABLE orders DROP COLUMN legacy_status;
CREATE INDEX idx_orders_customer ON orders (customer_id);

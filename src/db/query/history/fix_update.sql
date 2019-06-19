UPDATE history 
SET 
	update_time = %s,
	price_close = %s,
	pl = %s
WHERE
	trade_id = %s;

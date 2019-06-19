UPDATE history 
SET 
	create_time = %s,
	update_time = %s,
	price_close = %s,
	pl = %s,
	memo = %s 
WHERE
	trade_id = %s;

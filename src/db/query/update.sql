UPDATE history 
SET 
	update_time = %s,
	price_close = %s,
	pl = %s,
	event_close_id = %s
WHERE
	trade_id = %s;

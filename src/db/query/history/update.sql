UPDATE history 
SET 
	update_time = %s,
	event_close_id = %s,
	state = %s
WHERE
	trade_id = %s;

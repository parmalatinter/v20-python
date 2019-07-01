UPDATE history 
SET 
	update_time = %(update_time)s,
	event_close_id = %(event_close_id)s,
	state = %(state)s
WHERE
	trade_id = %(trade_id)s;
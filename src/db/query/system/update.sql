UPDATE system 
SET 
	update_time = %s,
	balance = %s,
	pl = %s,
	pl_percent = %s,
	win_count = %s,
	lose_count = %s,
	trade_count = %s
WHERE
	create_time > now() - interval '1 day'
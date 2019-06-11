UPDATE system 
SET 
	update_time = %s,
	balance = %s,
	win_count = %s,
	lose_count = %s,
	trade_count = %s
WHERE
	create_time > now() - interval '1 day'
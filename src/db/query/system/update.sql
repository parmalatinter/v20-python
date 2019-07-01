UPDATE system 
SET 
	update_time = '%(update_time)s',
	balance = %(balance)s,
	pl = %(pl)s,
	unrealized_pl = %(unrealized_pl)s,
	pl_percent = %(pl_percent)s,
	win_count = %(win_count)s,
	lose_count = %(lose_count)s,
	trade_count = %(trade_count)s
WHERE
	create_time > now() - interval '1 day'
UPDATE system 
SET 
	update_time = %(update_time)s,
	pl =%(pl)s,
	unrealized_pl = %(unrealized_pl)s,
	win_count = %(win_count)s,
	lose_count = %(lose_count)s
WHERE
	create_time > now() - interval '1 day'
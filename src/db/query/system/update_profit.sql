UPDATE system 
SET 
	update_time = %s,
	pl = %s,
	unrealized_pl = %s
WHERE
	create_time > now() - interval '1 day'
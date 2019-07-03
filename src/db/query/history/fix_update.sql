UPDATE history 
SET 
	update_time = '%(update_time)s',
	price_close = %(price_close)s,
	pl = %(pl)s,
	memo = '%(memo)s'
WHERE
	trade_id = %(trade_id)s
	AND pl IS NULL;

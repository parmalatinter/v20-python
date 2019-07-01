INSERT INTO system
    (	
		balance,
		pl,
		pl_percent,
		win_count,
		lose_count,
		trade_count,
		create_time
	)
SELECT 
	%(balance)s,
	%(pl)s,
	%(pl_percent)s,
	%(win_count)s,
	%(lose_count)s,
	%(trade_count)s,
	%(create_time)s
WHERE
    NOT EXISTS (
        SELECT id FROM system WHERE create_time > now() - interval '1 day'
    );
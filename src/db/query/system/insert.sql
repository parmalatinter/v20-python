INSERT INTO system
    (	
    	balance,
		win_count,
		lose_count,
		trade_count,
		create_time
	)
SELECT %s,%s,%s,%s,%s
WHERE
    NOT EXISTS (
        SELECT id FROM system WHERE create_time > now() - interval '1 day'
    );
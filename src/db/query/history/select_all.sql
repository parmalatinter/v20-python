SELECT
	id,
    trade_id,
	create_time,
	update_time,
	state,
	instrument,
	units,
	pl,
	price,
	price_target,
	price_close,
	event_open_id,
	event_close_id,
	memo,
	judge_1,
	judge_2,
	rule_1,
	rule_2,
	rule_3,
	rule_4,
	rule_5,
	rule_6,
	resistance_high,
	resistance_low
	trend_1,
	trend_2,
	trend_3,
	trend_4,
	trend_cal
FROM history ORDER BY trade_id;
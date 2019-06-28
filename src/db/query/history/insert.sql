INSERT INTO history (
	trade_id,
	create_time,
	price,
	price_target,
	state,
	instrument,
	units,
	unrealized_pl,
	event_open_id,
	trend_1,
	trend_2,
	trend_3,
	trend_4,
	trend_cal,
	judge_1,
	judge_2,
	rule_1,
	rule_2,
	rule_3,
	rule_4,
	rule_5,
	rule_6,
	memo,
	event_close_id
) VALUES (
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	%s,
	0
)

INSERT INTO history (
	trade_id,
	create_time,
	price,
	state,
	instrument,
	units,
	unrealized_pl,
	event_open_id,
	trend,
	judge_1,
	judge_2
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
	%s
)

CREATE TABLE IF NOT EXISTS system (
	id serial PRIMARY KEY,
	balance integer,
	pl integer,
	pl_percent numeric,
	unrealized_pl numeric,
	win_count integer,
	lose_count integer,
	trade_count integer,
	create_time timestamp default CURRENT_TIMESTAMP,
	update_time timestamp
)
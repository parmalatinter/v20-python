CREATE TABLE IF NOT EXISTS history (
	id serial PRIMARY KEY,
	trade_id integer,
	create_time timestamp default CURRENT_TIMESTAMP,
	update_time timestamp,
	price numeric,
	price_close numeric,
	state varchar,
	instrument varchar,
	units numeric,
	unrealized_pl numeric,
	pl numeric,
	event_open_id integer,
	event_close_id integer,
	trend numeric,
	judge_1 boolean,
	judge_2 boolean
)
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: hstore; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS hstore WITH SCHEMA public;


--
-- Name: EXTENSION hstore; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION hstore IS 'data type for storing sets of (key, value) pairs';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: ar_internal_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ar_internal_metadata (
    key character varying NOT NULL,
    value character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: blueprint_materials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blueprint_materials (
    id integer NOT NULL,
    blueprint_id integer NOT NULL,
    required_qtt integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    eve_item_id bigint NOT NULL
);


--
-- Name: blueprint_materials_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blueprint_materials_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blueprint_materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blueprint_materials_id_seq OWNED BY public.blueprint_materials.id;


--
-- Name: blueprint_modifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blueprint_modifications (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    blueprint_id bigint NOT NULL,
    percent_modification_value double precision NOT NULL,
    touched boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: blueprint_modifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blueprint_modifications_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blueprint_modifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blueprint_modifications_id_seq OWNED BY public.blueprint_modifications.id;


--
-- Name: blueprints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blueprints (
    id integer NOT NULL,
    produced_cpp_type_id integer NOT NULL,
    nb_runs integer NOT NULL,
    prod_qtt integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    cpp_blueprint_id integer NOT NULL,
    name character varying NOT NULL
);


--
-- Name: blueprints_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blueprints_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blueprints_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blueprints_id_seq OWNED BY public.blueprints.id;


--
-- Name: bpc_assets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bpc_assets (
    id bigint NOT NULL,
    station_detail_id bigint,
    quantity bigint NOT NULL,
    touched boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    user_id bigint NOT NULL,
    eve_item_id bigint NOT NULL
);


--
-- Name: bpc_assets_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bpc_assets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bpc_assets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bpc_assets_id_seq OWNED BY public.bpc_assets.id;


--
-- Name: bpc_assets_stations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bpc_assets_stations (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    station_detail_id bigint NOT NULL,
    touched boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: bpc_assets_stations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bpc_assets_stations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bpc_assets_stations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bpc_assets_stations_id_seq OWNED BY public.bpc_assets_stations.id;


--
-- Name: buy_orders_analytics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.buy_orders_analytics (
    id bigint NOT NULL,
    trade_hub_id bigint NOT NULL,
    eve_item_id bigint NOT NULL,
    approx_max_price double precision,
    over_approx_max_price_volume bigint,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    single_unit_cost double precision,
    single_unit_margin double precision,
    estimated_volume_margin double precision,
    per_job_margin double precision,
    per_job_run_margin double precision,
    final_margin double precision
);


--
-- Name: buy_orders_analytics_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.buy_orders_analytics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: buy_orders_analytics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.buy_orders_analytics_id_seq OWNED BY public.buy_orders_analytics.id;


--
-- Name: eve_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.eve_items (
    id integer NOT NULL,
    cpp_eve_item_id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    cost double precision,
    market_group_id integer,
    blueprint_id bigint,
    volume double precision,
    production_level integer DEFAULT 0 NOT NULL,
    base_item boolean DEFAULT false NOT NULL,
    cpp_market_adjusted_price double precision,
    cpp_market_average_price double precision,
    description character varying,
    market_group_path json DEFAULT '[]'::json NOT NULL,
    mass double precision,
    packaged_volume double precision,
    weekly_avg_price double precision,
    faction boolean DEFAULT false NOT NULL
);


--
-- Name: eve_items_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.eve_items_users (
    id integer NOT NULL,
    user_id integer,
    eve_item_id integer
);


--
-- Name: regions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.regions (
    id integer NOT NULL,
    cpp_region_id character varying NOT NULL,
    name character varying NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: trade_hubs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.trade_hubs (
    id integer NOT NULL,
    eve_system_id integer NOT NULL,
    name character varying(255) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    region_id integer,
    "inner" boolean DEFAULT false NOT NULL
);


--
-- Name: trade_hubs_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.trade_hubs_users (
    id integer NOT NULL,
    user_id integer,
    trade_hub_id integer
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying(255),
    remove_occuped_places boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    provider character varying(255),
    uid character varying(255),
    last_changes_in_choices timestamp without time zone,
    min_pcent_for_advice integer,
    watch_my_prices boolean,
    min_amount_for_advice double precision,
    admin boolean DEFAULT false NOT NULL,
    batch_cap boolean DEFAULT true NOT NULL,
    vol_month_pcent integer DEFAULT 10 NOT NULL,
    expires_on timestamp without time zone,
    token character varying,
    renew_token character varying,
    locked boolean DEFAULT false NOT NULL,
    download_assets_running boolean DEFAULT false NOT NULL,
    last_assets_download timestamp without time zone,
    download_orders_running boolean DEFAULT false NOT NULL,
    last_orders_download timestamp without time zone,
    batch_cap_multiplier integer DEFAULT 1 NOT NULL,
    last_duplication_receiver_id integer,
    selected_assets_station_id bigint,
    download_blueprints_running boolean DEFAULT false NOT NULL,
    last_blueprints_download timestamp without time zone,
    sales_orders_show_margin_min integer
);


--
-- Name: buy_orders_analytics_results; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.buy_orders_analytics_results AS
 SELECT boa.id,
    u.id AS user_id,
    boa.trade_hub_id,
    boa.eve_item_id,
    ((((tu.name)::text || ' ('::text) || (r.name)::text) || ')'::text) AS trade_hub_name,
    ei.name AS eve_item_name,
    boa.approx_max_price,
    boa.single_unit_cost,
    boa.single_unit_margin,
    boa.final_margin,
    boa.per_job_margin,
    ceil((boa.final_margin / boa.per_job_margin)) AS job_count,
    boa.per_job_run_margin,
    floor((boa.final_margin / boa.per_job_run_margin)) AS runs,
    (floor((boa.final_margin / boa.per_job_run_margin)) * boa.per_job_run_margin) AS true_margin,
    boa.estimated_volume_margin,
    boa.over_approx_max_price_volume
   FROM ((((((public.buy_orders_analytics boa
     JOIN public.eve_items ei ON ((ei.id = boa.eve_item_id)))
     JOIN public.trade_hubs tu ON ((boa.trade_hub_id = tu.id)))
     JOIN public.trade_hubs_users thu ON ((boa.trade_hub_id = thu.trade_hub_id)))
     JOIN public.eve_items_users eiu ON ((boa.eve_item_id = eiu.eve_item_id)))
     JOIN public.users u ON (((thu.user_id = u.id) AND (eiu.user_id = u.id))))
     JOIN public.regions r ON ((tu.region_id = r.id)))
  WHERE (boa.final_margin > (0)::double precision)
  ORDER BY boa.final_margin DESC;


--
-- Name: components_to_buys; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.components_to_buys AS
SELECT
    NULL::integer AS id,
    NULL::integer AS user_id,
    NULL::character varying(255) AS eve_item_name,
    NULL::integer AS eve_item_id,
    NULL::double precision AS qtt_to_buy,
    NULL::double precision AS total_cost,
    NULL::double precision AS required_volume,
    NULL::boolean AS base_item;


--
-- Name: crontabs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.crontabs (
    id bigint NOT NULL,
    cron_name character varying NOT NULL,
    status boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: crontabs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.crontabs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: crontabs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.crontabs_id_seq OWNED BY public.crontabs.id;


--
-- Name: eve_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.eve_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: eve_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.eve_items_id_seq OWNED BY public.eve_items.id;


--
-- Name: eve_items_saved_lists; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.eve_items_saved_lists (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    description character varying NOT NULL,
    saved_ids character varying NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: eve_items_saved_lists_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.eve_items_saved_lists_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: eve_items_saved_lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.eve_items_saved_lists_id_seq OWNED BY public.eve_items_saved_lists.id;


--
-- Name: eve_items_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.eve_items_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: eve_items_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.eve_items_users_id_seq OWNED BY public.eve_items_users.id;


--
-- Name: eve_market_volumes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.eve_market_volumes (
    id bigint NOT NULL,
    region_id bigint NOT NULL,
    eve_item_id bigint NOT NULL,
    volume bigint NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: eve_market_volumes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.eve_market_volumes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: eve_market_volumes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.eve_market_volumes_id_seq OWNED BY public.eve_market_volumes.id;


--
-- Name: identities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.identities (
    id integer NOT NULL,
    name character varying(255),
    email character varying(255),
    password_digest character varying(255),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: identities_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.identities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: identities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.identities_id_seq OWNED BY public.identities.id;


--
-- Name: last_updates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.last_updates (
    id bigint NOT NULL,
    update_type character varying NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: last_updates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.last_updates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: last_updates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.last_updates_id_seq OWNED BY public.last_updates.id;


--
-- Name: market_group_hierarchies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.market_group_hierarchies (
    ancestor_id integer NOT NULL,
    descendant_id integer NOT NULL,
    generations integer NOT NULL
);


--
-- Name: market_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.market_groups (
    id integer NOT NULL,
    name character varying NOT NULL,
    parent_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    cpp_market_group_id integer NOT NULL,
    cpp_parent_market_group_id integer
);


--
-- Name: market_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.market_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: market_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.market_groups_id_seq OWNED BY public.market_groups.id;


--
-- Name: prices_advices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prices_advices (
    id integer NOT NULL,
    eve_item_id integer NOT NULL,
    trade_hub_id integer NOT NULL,
    vol_month bigint,
    avg_price_month double precision,
    immediate_montly_pcent real,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    margin_percent double precision,
    avg_price_week double precision
);


--
-- Name: prices_mins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prices_mins (
    id integer NOT NULL,
    eve_item_id integer,
    trade_hub_id integer,
    min_price double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    volume bigint
);


--
-- Name: price_advice_margin_comps; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.price_advice_margin_comps AS
 SELECT prices_advices_sub_1.id,
    prices_advices_sub_1.user_id,
    prices_advices_sub_1.item_id,
    prices_advices_sub_1.trade_hub_id,
    prices_advices_sub_1.region_name,
    prices_advices_sub_1.trade_hub_name,
    prices_advices_sub_1.item_name,
    prices_advices_sub_1.single_unit_cost,
    prices_advices_sub_1.min_price,
    prices_advices_sub_1.price_avg_week,
    prices_advices_sub_1.vol_month,
    prices_advices_sub_1.full_batch_size,
    prices_advices_sub_1.daily_monthly_pcent,
    prices_advices_sub_1.margin_percent,
    prices_advices_sub_1.batch_size_formula,
    prices_advices_sub_1.min_amount_for_advice,
    prices_advices_sub_1.min_pcent_for_advice,
    ((prices_advices_sub_1.min_price * (prices_advices_sub_1.batch_size_formula)::double precision) - (prices_advices_sub_1.single_unit_cost * (prices_advices_sub_1.batch_size_formula)::double precision)) AS margin_comp_immediate,
    ((prices_advices_sub_1.price_avg_week * (prices_advices_sub_1.batch_size_formula)::double precision) - (prices_advices_sub_1.single_unit_cost * (prices_advices_sub_1.batch_size_formula)::double precision)) AS margin_comp_weekly
   FROM ( SELECT pa.id,
            ur.id AS user_id,
            ei.id AS item_id,
            tu.id AS trade_hub_id,
            re.name AS region_name,
            tu.name AS trade_hub_name,
            ei.name AS item_name,
            ei.cost AS single_unit_cost,
            pm.min_price,
            ei.weekly_avg_price AS price_avg_week,
            pa.vol_month,
            (bp.nb_runs * bp.prod_qtt) AS full_batch_size,
            pa.immediate_montly_pcent AS daily_monthly_pcent,
            pa.margin_percent,
                CASE
                    WHEN ur.batch_cap THEN LEAST((((bp.nb_runs * bp.prod_qtt) * ur.batch_cap_multiplier))::numeric, floor((((pa.vol_month * ur.vol_month_pcent))::numeric * 0.01)))
                    ELSE floor((((pa.vol_month * ur.vol_month_pcent))::numeric * 0.01))
                END AS batch_size_formula,
            ur.min_amount_for_advice,
            ur.min_pcent_for_advice
           FROM ((((((((public.prices_advices pa
             JOIN public.eve_items ei ON ((pa.eve_item_id = ei.id)))
             JOIN public.blueprints bp ON ((ei.blueprint_id = bp.id)))
             JOIN public.trade_hubs tu ON ((pa.trade_hub_id = tu.id)))
             JOIN public.regions re ON ((re.id = tu.region_id)))
             JOIN public.trade_hubs_users thu ON ((thu.trade_hub_id = pa.trade_hub_id)))
             JOIN public.eve_items_users eiu ON ((eiu.eve_item_id = pa.eve_item_id)))
             JOIN public.users ur ON ((thu.user_id = ur.id)))
             JOIN public.prices_mins pm ON (((pm.trade_hub_id = pa.trade_hub_id) AND (pa.eve_item_id = pm.eve_item_id))))
          WHERE ((pa.vol_month IS NOT NULL) AND (ur.id = eiu.user_id))) prices_advices_sub_1;


--
-- Name: price_advices_min_prices; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.price_advices_min_prices AS
 SELECT pa.id,
    ei.id AS eve_item_id,
    tu.id AS trade_hub_id,
    ((((tu.name)::text || ' ('::text) || (re.name)::text) || ')'::text) AS trade_hub_name,
    ei.name AS item_name,
    ei.cost,
    pm.min_price,
    pa.avg_price_week,
    pa.avg_price_month,
    pa.vol_month,
    (bp.nb_runs * bp.prod_qtt) AS full_batch_size,
    pa.immediate_montly_pcent,
    pa.margin_percent,
    ((pa.avg_price_month / ei.cost) - (1)::double precision) AS avg_monthly_margin_percent
   FROM (((((public.prices_advices pa
     JOIN public.eve_items ei ON ((pa.eve_item_id = ei.id)))
     JOIN public.blueprints bp ON ((ei.blueprint_id = bp.id)))
     JOIN public.trade_hubs tu ON ((pa.trade_hub_id = tu.id)))
     JOIN public.regions re ON ((re.id = tu.region_id)))
     LEFT JOIN public.prices_mins pm ON (((pm.trade_hub_id = pa.trade_hub_id) AND (pa.eve_item_id = pm.eve_item_id))));


--
-- Name: prices_advices_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.prices_advices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: prices_advices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.prices_advices_id_seq OWNED BY public.prices_advices.id;


--
-- Name: prices_mins_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.prices_mins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: prices_mins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.prices_mins_id_seq OWNED BY public.prices_mins.id;


--
-- Name: production_lists; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.production_lists (
    id integer NOT NULL,
    user_id integer NOT NULL,
    trade_hub_id integer NOT NULL,
    eve_item_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    runs_count smallint
);


--
-- Name: production_lists_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.production_lists_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: production_lists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.production_lists_id_seq OWNED BY public.production_lists.id;


--
-- Name: public_trade_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.public_trade_orders (
    id bigint NOT NULL,
    trade_hub_id bigint NOT NULL,
    eve_item_id bigint NOT NULL,
    order_id bigint NOT NULL,
    is_buy_order boolean NOT NULL,
    end_time timestamp without time zone NOT NULL,
    price double precision NOT NULL,
    range character varying NOT NULL,
    volume_remain bigint NOT NULL,
    volume_total bigint NOT NULL,
    min_volume bigint NOT NULL,
    touched boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: public_trade_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.public_trade_orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: public_trade_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.public_trade_orders_id_seq OWNED BY public.public_trade_orders.id;


--
-- Name: regions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.regions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: regions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.regions_id_seq OWNED BY public.regions.id;


--
-- Name: sales_finals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sales_finals (
    id bigint NOT NULL,
    day date NOT NULL,
    trade_hub_id bigint NOT NULL,
    eve_item_id bigint NOT NULL,
    volume bigint NOT NULL,
    price double precision NOT NULL,
    order_id bigint NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: sales_finals_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sales_finals_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sales_finals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sales_finals_id_seq OWNED BY public.sales_finals.id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(255) NOT NULL
);


--
-- Name: station_details; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.station_details (
    id bigint NOT NULL,
    cpp_system_id integer NOT NULL,
    cpp_station_id integer NOT NULL,
    name character varying NOT NULL,
    services character varying[] NOT NULL,
    office_rental_cost double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    station_id bigint,
    security_status double precision,
    jita_distance smallint,
    industry_costs_indices public.hstore
);


--
-- Name: station_details_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.station_details_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: station_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.station_details_id_seq OWNED BY public.station_details.id;


--
-- Name: stations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stations (
    id integer NOT NULL,
    trade_hub_id integer,
    name character varying(255),
    cpp_station_id integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: stations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stations_id_seq OWNED BY public.stations.id;


--
-- Name: structures; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.structures (
    id bigint NOT NULL,
    cpp_structure_id bigint NOT NULL,
    trade_hub_id bigint,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    forbidden boolean DEFAULT true NOT NULL
);


--
-- Name: structures_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.structures_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: structures_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.structures_id_seq OWNED BY public.structures.id;


--
-- Name: trade_hubs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.trade_hubs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: trade_hubs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.trade_hubs_id_seq OWNED BY public.trade_hubs.id;


--
-- Name: trade_hubs_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.trade_hubs_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: trade_hubs_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.trade_hubs_users_id_seq OWNED BY public.trade_hubs_users.id;


--
-- Name: user_activity_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_activity_logs (
    id integer NOT NULL,
    ip character varying,
    action character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    "user" character varying
);


--
-- Name: user_activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_activity_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_activity_logs_id_seq OWNED BY public.user_activity_logs.id;


--
-- Name: user_sale_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_sale_orders (
    id integer NOT NULL,
    user_id integer NOT NULL,
    eve_item_id integer NOT NULL,
    trade_hub_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    price double precision NOT NULL
);


--
-- Name: user_sale_order_details; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.user_sale_order_details AS
 SELECT uso.id,
    uso.user_id,
    ((((tu.name)::text || ' ('::text) || (r.name)::text) || ')'::text) AS trade_hub_name,
    ei.name AS eve_item_name,
    uso.price AS my_price,
    pm.min_price,
    ei.cost,
    b.prod_qtt,
    ((pm.min_price / ei.cost) - (1)::double precision) AS min_price_margin_pcent,
    (pm.min_price - uso.price) AS price_delta,
    uso.eve_item_id,
    uso.trade_hub_id,
    ei.cpp_eve_item_id,
    tu.eve_system_id
   FROM (((((public.user_sale_orders uso
     JOIN public.eve_items ei ON ((ei.id = uso.eve_item_id)))
     JOIN public.blueprints b ON ((ei.blueprint_id = b.id)))
     JOIN public.trade_hubs tu ON ((uso.trade_hub_id = tu.id)))
     JOIN public.regions r ON ((tu.region_id = r.id)))
     LEFT JOIN public.prices_mins pm ON (((pm.eve_item_id = uso.eve_item_id) AND (pm.trade_hub_id = uso.trade_hub_id))));


--
-- Name: user_sale_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_sale_orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_sale_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_sale_orders_id_seq OWNED BY public.user_sale_orders.id;


--
-- Name: user_to_user_duplication_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_to_user_duplication_requests (
    id bigint NOT NULL,
    sender_id integer NOT NULL,
    receiver_id integer NOT NULL,
    duplication_type smallint NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: user_to_user_duplication_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_to_user_duplication_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_to_user_duplication_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_to_user_duplication_requests_id_seq OWNED BY public.user_to_user_duplication_requests.id;


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: weekly_price_details; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.weekly_price_details (
    id bigint NOT NULL,
    eve_item_id bigint NOT NULL,
    day date NOT NULL,
    volume double precision NOT NULL,
    weighted_avg_price double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    trade_hub_id bigint NOT NULL
);


--
-- Name: weekly_price_details_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.weekly_price_details_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: weekly_price_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.weekly_price_details_id_seq OWNED BY public.weekly_price_details.id;


--
-- Name: blueprint_materials id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_materials ALTER COLUMN id SET DEFAULT nextval('public.blueprint_materials_id_seq'::regclass);


--
-- Name: blueprint_modifications id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_modifications ALTER COLUMN id SET DEFAULT nextval('public.blueprint_modifications_id_seq'::regclass);


--
-- Name: blueprints id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprints ALTER COLUMN id SET DEFAULT nextval('public.blueprints_id_seq'::regclass);


--
-- Name: bpc_assets id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets ALTER COLUMN id SET DEFAULT nextval('public.bpc_assets_id_seq'::regclass);


--
-- Name: bpc_assets_stations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets_stations ALTER COLUMN id SET DEFAULT nextval('public.bpc_assets_stations_id_seq'::regclass);


--
-- Name: buy_orders_analytics id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.buy_orders_analytics ALTER COLUMN id SET DEFAULT nextval('public.buy_orders_analytics_id_seq'::regclass);


--
-- Name: crontabs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crontabs ALTER COLUMN id SET DEFAULT nextval('public.crontabs_id_seq'::regclass);


--
-- Name: eve_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items ALTER COLUMN id SET DEFAULT nextval('public.eve_items_id_seq'::regclass);


--
-- Name: eve_items_saved_lists id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items_saved_lists ALTER COLUMN id SET DEFAULT nextval('public.eve_items_saved_lists_id_seq'::regclass);


--
-- Name: eve_items_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items_users ALTER COLUMN id SET DEFAULT nextval('public.eve_items_users_id_seq'::regclass);


--
-- Name: eve_market_volumes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_market_volumes ALTER COLUMN id SET DEFAULT nextval('public.eve_market_volumes_id_seq'::regclass);


--
-- Name: identities id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.identities ALTER COLUMN id SET DEFAULT nextval('public.identities_id_seq'::regclass);


--
-- Name: last_updates id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.last_updates ALTER COLUMN id SET DEFAULT nextval('public.last_updates_id_seq'::regclass);


--
-- Name: market_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.market_groups ALTER COLUMN id SET DEFAULT nextval('public.market_groups_id_seq'::regclass);


--
-- Name: prices_advices id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_advices ALTER COLUMN id SET DEFAULT nextval('public.prices_advices_id_seq'::regclass);


--
-- Name: prices_mins id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_mins ALTER COLUMN id SET DEFAULT nextval('public.prices_mins_id_seq'::regclass);


--
-- Name: production_lists id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_lists ALTER COLUMN id SET DEFAULT nextval('public.production_lists_id_seq'::regclass);


--
-- Name: public_trade_orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_trade_orders ALTER COLUMN id SET DEFAULT nextval('public.public_trade_orders_id_seq'::regclass);


--
-- Name: regions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.regions ALTER COLUMN id SET DEFAULT nextval('public.regions_id_seq'::regclass);


--
-- Name: sales_finals id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_finals ALTER COLUMN id SET DEFAULT nextval('public.sales_finals_id_seq'::regclass);


--
-- Name: station_details id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_details ALTER COLUMN id SET DEFAULT nextval('public.station_details_id_seq'::regclass);


--
-- Name: stations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stations ALTER COLUMN id SET DEFAULT nextval('public.stations_id_seq'::regclass);


--
-- Name: structures id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.structures ALTER COLUMN id SET DEFAULT nextval('public.structures_id_seq'::regclass);


--
-- Name: trade_hubs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade_hubs ALTER COLUMN id SET DEFAULT nextval('public.trade_hubs_id_seq'::regclass);


--
-- Name: trade_hubs_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade_hubs_users ALTER COLUMN id SET DEFAULT nextval('public.trade_hubs_users_id_seq'::regclass);


--
-- Name: user_activity_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_activity_logs ALTER COLUMN id SET DEFAULT nextval('public.user_activity_logs_id_seq'::regclass);


--
-- Name: user_sale_orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sale_orders ALTER COLUMN id SET DEFAULT nextval('public.user_sale_orders_id_seq'::regclass);


--
-- Name: user_to_user_duplication_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_to_user_duplication_requests ALTER COLUMN id SET DEFAULT nextval('public.user_to_user_duplication_requests_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: weekly_price_details id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weekly_price_details ALTER COLUMN id SET DEFAULT nextval('public.weekly_price_details_id_seq'::regclass);


--
-- Name: ar_internal_metadata ar_internal_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ar_internal_metadata
    ADD CONSTRAINT ar_internal_metadata_pkey PRIMARY KEY (key);


--
-- Name: blueprint_materials blueprint_materials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_materials
    ADD CONSTRAINT blueprint_materials_pkey PRIMARY KEY (id);


--
-- Name: blueprint_modifications blueprint_modifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_modifications
    ADD CONSTRAINT blueprint_modifications_pkey PRIMARY KEY (id);


--
-- Name: blueprints blueprints_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprints
    ADD CONSTRAINT blueprints_pkey PRIMARY KEY (id);


--
-- Name: bpc_assets bpc_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets
    ADD CONSTRAINT bpc_assets_pkey PRIMARY KEY (id);


--
-- Name: bpc_assets_stations bpc_assets_stations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets_stations
    ADD CONSTRAINT bpc_assets_stations_pkey PRIMARY KEY (id);


--
-- Name: buy_orders_analytics buy_orders_analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.buy_orders_analytics
    ADD CONSTRAINT buy_orders_analytics_pkey PRIMARY KEY (id);


--
-- Name: crontabs crontabs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crontabs
    ADD CONSTRAINT crontabs_pkey PRIMARY KEY (id);


--
-- Name: eve_items eve_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items
    ADD CONSTRAINT eve_items_pkey PRIMARY KEY (id);


--
-- Name: eve_items_saved_lists eve_items_saved_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items_saved_lists
    ADD CONSTRAINT eve_items_saved_lists_pkey PRIMARY KEY (id);


--
-- Name: eve_items_users eve_items_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items_users
    ADD CONSTRAINT eve_items_users_pkey PRIMARY KEY (id);


--
-- Name: eve_market_volumes eve_market_volumes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_market_volumes
    ADD CONSTRAINT eve_market_volumes_pkey PRIMARY KEY (id);


--
-- Name: identities identities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.identities
    ADD CONSTRAINT identities_pkey PRIMARY KEY (id);


--
-- Name: last_updates last_updates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.last_updates
    ADD CONSTRAINT last_updates_pkey PRIMARY KEY (id);


--
-- Name: market_groups market_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.market_groups
    ADD CONSTRAINT market_groups_pkey PRIMARY KEY (id);


--
-- Name: prices_advices prices_advices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_advices
    ADD CONSTRAINT prices_advices_pkey PRIMARY KEY (id);


--
-- Name: prices_mins prices_mins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_mins
    ADD CONSTRAINT prices_mins_pkey PRIMARY KEY (id);


--
-- Name: production_lists production_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_lists
    ADD CONSTRAINT production_lists_pkey PRIMARY KEY (id);


--
-- Name: public_trade_orders public_trade_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_trade_orders
    ADD CONSTRAINT public_trade_orders_pkey PRIMARY KEY (id);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (id);


--
-- Name: sales_finals sales_finals_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_finals
    ADD CONSTRAINT sales_finals_pkey PRIMARY KEY (id);


--
-- Name: station_details station_details_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_details
    ADD CONSTRAINT station_details_pkey PRIMARY KEY (id);


--
-- Name: stations stations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stations
    ADD CONSTRAINT stations_pkey PRIMARY KEY (id);


--
-- Name: structures structures_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.structures
    ADD CONSTRAINT structures_pkey PRIMARY KEY (id);


--
-- Name: trade_hubs trade_hubs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade_hubs
    ADD CONSTRAINT trade_hubs_pkey PRIMARY KEY (id);


--
-- Name: trade_hubs_users trade_hubs_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade_hubs_users
    ADD CONSTRAINT trade_hubs_users_pkey PRIMARY KEY (id);


--
-- Name: user_activity_logs user_activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_activity_logs
    ADD CONSTRAINT user_activity_logs_pkey PRIMARY KEY (id);


--
-- Name: user_sale_orders user_sale_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sale_orders
    ADD CONSTRAINT user_sale_orders_pkey PRIMARY KEY (id);


--
-- Name: user_to_user_duplication_requests user_to_user_duplication_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_to_user_duplication_requests
    ADD CONSTRAINT user_to_user_duplication_requests_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: weekly_price_details weekly_price_details_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weekly_price_details
    ADD CONSTRAINT weekly_price_details_pkey PRIMARY KEY (id);


--
-- Name: index_blueprint_materials_on_blueprint_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_blueprint_materials_on_blueprint_id ON public.blueprint_materials USING btree (blueprint_id);


--
-- Name: index_blueprint_materials_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_blueprint_materials_on_eve_item_id ON public.blueprint_materials USING btree (eve_item_id);


--
-- Name: index_blueprint_modifications_on_user_id_and_blueprint_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_blueprint_modifications_on_user_id_and_blueprint_id ON public.blueprint_modifications USING btree (user_id, blueprint_id);


--
-- Name: index_blueprints_on_cpp_blueprint_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_blueprints_on_cpp_blueprint_id ON public.blueprints USING btree (cpp_blueprint_id);


--
-- Name: index_blueprints_on_produced_cpp_type_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_blueprints_on_produced_cpp_type_id ON public.blueprints USING btree (produced_cpp_type_id);


--
-- Name: index_bpc_assets_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_assets_on_eve_item_id ON public.bpc_assets USING btree (eve_item_id);


--
-- Name: index_bpc_assets_on_station_detail_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_assets_on_station_detail_id ON public.bpc_assets USING btree (station_detail_id);


--
-- Name: index_bpc_assets_stations_on_station_detail_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_assets_stations_on_station_detail_id ON public.bpc_assets_stations USING btree (station_detail_id);


--
-- Name: index_bpc_assets_stations_on_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_assets_stations_on_user_id ON public.bpc_assets_stations USING btree (user_id);


--
-- Name: index_buy_orders_analytics_on_eve_item_id_and_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_buy_orders_analytics_on_eve_item_id_and_trade_hub_id ON public.buy_orders_analytics USING btree (eve_item_id, trade_hub_id);


--
-- Name: index_eve_items_on_blueprint_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_items_on_blueprint_id ON public.eve_items USING btree (blueprint_id);


--
-- Name: index_eve_items_on_cpp_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_items_on_cpp_eve_item_id ON public.eve_items USING btree (cpp_eve_item_id);


--
-- Name: index_eve_items_on_lower_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_eve_items_on_lower_name ON public.eve_items USING btree (lower((name)::text));


--
-- Name: index_eve_items_on_market_group_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_items_on_market_group_id ON public.eve_items USING btree (market_group_id);


--
-- Name: index_eve_items_saved_lists_on_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_items_saved_lists_on_user_id ON public.eve_items_saved_lists USING btree (user_id);


--
-- Name: index_eve_items_users_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_items_users_on_eve_item_id ON public.eve_items_users USING btree (eve_item_id);


--
-- Name: index_eve_items_users_on_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_items_users_on_user_id ON public.eve_items_users USING btree (user_id);


--
-- Name: index_eve_market_volumes_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_market_volumes_on_eve_item_id ON public.eve_market_volumes USING btree (eve_item_id);


--
-- Name: index_eve_market_volumes_on_region_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_market_volumes_on_region_id ON public.eve_market_volumes USING btree (region_id);


--
-- Name: index_market_groups_on_cpp_market_group_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_market_groups_on_cpp_market_group_id ON public.market_groups USING btree (cpp_market_group_id);


--
-- Name: index_prices_advices_on_eve_item_id_and_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_prices_advices_on_eve_item_id_and_trade_hub_id ON public.prices_advices USING btree (eve_item_id, trade_hub_id);


--
-- Name: index_prices_advices_on_margin_percent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_prices_advices_on_margin_percent ON public.prices_advices USING btree (margin_percent);


--
-- Name: index_prices_mins_on_eve_item_id_and_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_prices_mins_on_eve_item_id_and_trade_hub_id ON public.prices_mins USING btree (eve_item_id, trade_hub_id);


--
-- Name: index_production_lists_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_production_lists_on_eve_item_id ON public.production_lists USING btree (eve_item_id);


--
-- Name: index_production_lists_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_production_lists_on_trade_hub_id ON public.production_lists USING btree (trade_hub_id);


--
-- Name: index_production_lists_on_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_production_lists_on_user_id ON public.production_lists USING btree (user_id);


--
-- Name: index_public_trade_orders_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_public_trade_orders_on_eve_item_id ON public.public_trade_orders USING btree (eve_item_id);


--
-- Name: index_public_trade_orders_on_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_public_trade_orders_on_order_id ON public.public_trade_orders USING btree (order_id);


--
-- Name: index_public_trade_orders_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_public_trade_orders_on_trade_hub_id ON public.public_trade_orders USING btree (trade_hub_id);


--
-- Name: index_regions_on_cpp_region_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_regions_on_cpp_region_id ON public.regions USING btree (cpp_region_id);


--
-- Name: index_sales_finals_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_sales_finals_on_eve_item_id ON public.sales_finals USING btree (eve_item_id);


--
-- Name: index_sales_finals_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_sales_finals_on_trade_hub_id ON public.sales_finals USING btree (trade_hub_id);


--
-- Name: index_station_details_on_cpp_station_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_station_details_on_cpp_station_id ON public.station_details USING btree (cpp_station_id);


--
-- Name: index_station_details_on_station_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_station_details_on_station_id ON public.station_details USING btree (station_id);


--
-- Name: index_stations_on_cpp_station_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_stations_on_cpp_station_id ON public.stations USING btree (cpp_station_id);


--
-- Name: index_stations_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_stations_on_trade_hub_id ON public.stations USING btree (trade_hub_id);


--
-- Name: index_structures_on_forbidden; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_structures_on_forbidden ON public.structures USING btree (forbidden);


--
-- Name: index_structures_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_structures_on_trade_hub_id ON public.structures USING btree (trade_hub_id);


--
-- Name: index_trade_hubs_on_eve_system_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_trade_hubs_on_eve_system_id ON public.trade_hubs USING btree (eve_system_id);


--
-- Name: index_trade_hubs_on_region_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_trade_hubs_on_region_id ON public.trade_hubs USING btree (region_id);


--
-- Name: index_trade_hubs_users_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_trade_hubs_users_on_trade_hub_id ON public.trade_hubs_users USING btree (trade_hub_id);


--
-- Name: index_trade_hubs_users_on_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_trade_hubs_users_on_user_id ON public.trade_hubs_users USING btree (user_id);


--
-- Name: index_user_sale_orders_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_user_sale_orders_on_eve_item_id ON public.user_sale_orders USING btree (eve_item_id);


--
-- Name: index_user_sale_orders_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_user_sale_orders_on_trade_hub_id ON public.user_sale_orders USING btree (trade_hub_id);


--
-- Name: index_user_sale_orders_on_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_user_sale_orders_on_user_id ON public.user_sale_orders USING btree (user_id);


--
-- Name: index_user_to_user_duplication_requests_on_receiver_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_user_to_user_duplication_requests_on_receiver_id ON public.user_to_user_duplication_requests USING btree (receiver_id);


--
-- Name: index_user_to_user_duplication_requests_on_sender_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_user_to_user_duplication_requests_on_sender_id ON public.user_to_user_duplication_requests USING btree (sender_id);


--
-- Name: market_group_anc_desc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX market_group_anc_desc_idx ON public.market_group_hierarchies USING btree (ancestor_id, descendant_id, generations);


--
-- Name: market_group_desc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX market_group_desc_idx ON public.market_group_hierarchies USING btree (descendant_id);


--
-- Name: unique_schema_migrations; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX unique_schema_migrations ON public.schema_migrations USING btree (version);


--
-- Name: wpd_eve_item_id_trade_hub_id_day; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX wpd_eve_item_id_trade_hub_id_day ON public.weekly_price_details USING btree (eve_item_id, trade_hub_id, day);


--
-- Name: components_to_buys _RETURN; Type: RULE; Schema: public; Owner: -
--

CREATE OR REPLACE VIEW public.components_to_buys AS
 SELECT bpm_mat_ei.id,
    pl.user_id,
    bpm_mat_ei.name AS eve_item_name,
    bpm_mat_ei.id AS eve_item_id,
    (sum(qtt_comp.raw_qtt) - (COALESCE(ba.quantity, (0)::bigint))::double precision) AS qtt_to_buy,
    ((sum(qtt_comp.raw_qtt) - (COALESCE(ba.quantity, (0)::bigint))::double precision) * bpm_mat_ei.cost) AS total_cost,
    ((sum(qtt_comp.raw_qtt) - (COALESCE(ba.quantity, (0)::bigint))::double precision) * bpm_mat_ei.volume) AS required_volume,
    bpm_mat_ei.base_item
   FROM (((((((public.production_lists pl
     JOIN public.eve_items ei ON ((ei.id = pl.eve_item_id)))
     JOIN public.blueprints b ON ((ei.blueprint_id = b.id)))
     JOIN public.blueprint_materials bm ON ((b.id = bm.blueprint_id)))
     JOIN public.eve_items bpm_mat_ei ON ((bm.eve_item_id = bpm_mat_ei.id)))
     JOIN public.users ue ON ((pl.user_id = ue.id)))
     LEFT JOIN public.blueprint_modifications bmo ON (((b.id = bmo.blueprint_id) AND (bmo.user_id = pl.user_id))))
     LEFT JOIN public.bpc_assets ba ON (((bpm_mat_ei.id = ba.eve_item_id) AND (ba.station_detail_id = ue.selected_assets_station_id)))),
    LATERAL ( SELECT ceil((((bm.required_qtt * pl.runs_count))::double precision * COALESCE(bmo.percent_modification_value, (1)::double precision))) AS raw_qtt) qtt_comp
  WHERE (pl.runs_count > 0)
  GROUP BY bpm_mat_ei.id, pl.user_id, bpm_mat_ei.name, COALESCE(ba.quantity, (0)::bigint)
 HAVING ((sum(qtt_comp.raw_qtt) - (COALESCE(ba.quantity, (0)::bigint))::double precision) > (0)::double precision);


--
-- Name: eve_market_volumes fk_rails_01da9c4169; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_market_volumes
    ADD CONSTRAINT fk_rails_01da9c4169 FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: blueprint_materials fk_rails_0206fd6697; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_materials
    ADD CONSTRAINT fk_rails_0206fd6697 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: production_lists fk_rails_0a4a7e08c4; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_lists
    ADD CONSTRAINT fk_rails_0a4a7e08c4 FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: eve_items fk_rails_13331b0da7; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items
    ADD CONSTRAINT fk_rails_13331b0da7 FOREIGN KEY (blueprint_id) REFERENCES public.blueprints(id);


--
-- Name: blueprint_materials fk_rails_1495e1c405; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_materials
    ADD CONSTRAINT fk_rails_1495e1c405 FOREIGN KEY (blueprint_id) REFERENCES public.blueprints(id);


--
-- Name: production_lists fk_rails_1adb19f87b; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_lists
    ADD CONSTRAINT fk_rails_1adb19f87b FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: blueprint_modifications fk_rails_1e50239e23; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_modifications
    ADD CONSTRAINT fk_rails_1e50239e23 FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: eve_items fk_rails_25122e004f; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items
    ADD CONSTRAINT fk_rails_25122e004f FOREIGN KEY (market_group_id) REFERENCES public.market_groups(id);


--
-- Name: weekly_price_details fk_rails_31f6906097; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weekly_price_details
    ADD CONSTRAINT fk_rails_31f6906097 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: buy_orders_analytics fk_rails_35a8cb6031; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.buy_orders_analytics
    ADD CONSTRAINT fk_rails_35a8cb6031 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: structures fk_rails_38f8c90abc; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.structures
    ADD CONSTRAINT fk_rails_38f8c90abc FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: users fk_rails_3e0634e4d9; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_rails_3e0634e4d9 FOREIGN KEY (selected_assets_station_id) REFERENCES public.station_details(id);


--
-- Name: eve_items_saved_lists fk_rails_4097699761; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items_saved_lists
    ADD CONSTRAINT fk_rails_4097699761 FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_to_user_duplication_requests fk_rails_41225de714; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_to_user_duplication_requests
    ADD CONSTRAINT fk_rails_41225de714 FOREIGN KEY (receiver_id) REFERENCES public.users(id);


--
-- Name: bpc_assets fk_rails_5259447fe3; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets
    ADD CONSTRAINT fk_rails_5259447fe3 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: bpc_assets fk_rails_68943bf535; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets
    ADD CONSTRAINT fk_rails_68943bf535 FOREIGN KEY (station_detail_id) REFERENCES public.station_details(id);


--
-- Name: production_lists fk_rails_68e1aeac4d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_lists
    ADD CONSTRAINT fk_rails_68e1aeac4d FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: bpc_assets fk_rails_6a736a22f9; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets
    ADD CONSTRAINT fk_rails_6a736a22f9 FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: blueprint_modifications fk_rails_7744def0ba; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_modifications
    ADD CONSTRAINT fk_rails_7744def0ba FOREIGN KEY (blueprint_id) REFERENCES public.blueprints(id);


--
-- Name: sales_finals fk_rails_8d037fe800; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_finals
    ADD CONSTRAINT fk_rails_8d037fe800 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: user_sale_orders fk_rails_94365f7fb0; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sale_orders
    ADD CONSTRAINT fk_rails_94365f7fb0 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: bpc_assets_stations fk_rails_a00a2978d6; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets_stations
    ADD CONSTRAINT fk_rails_a00a2978d6 FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_to_user_duplication_requests fk_rails_aeda0a36f7; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_to_user_duplication_requests
    ADD CONSTRAINT fk_rails_aeda0a36f7 FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- Name: prices_advices fk_rails_b6b5f49d4d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_advices
    ADD CONSTRAINT fk_rails_b6b5f49d4d FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: bpc_assets_stations fk_rails_c219097b39; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets_stations
    ADD CONSTRAINT fk_rails_c219097b39 FOREIGN KEY (station_detail_id) REFERENCES public.station_details(id);


--
-- Name: prices_advices fk_rails_ccdf67e46e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_advices
    ADD CONSTRAINT fk_rails_ccdf67e46e FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: user_sale_orders fk_rails_cf4b559877; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sale_orders
    ADD CONSTRAINT fk_rails_cf4b559877 FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: eve_market_volumes fk_rails_cf61c48468; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_market_volumes
    ADD CONSTRAINT fk_rails_cf61c48468 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: user_sale_orders fk_rails_d8144e7823; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sale_orders
    ADD CONSTRAINT fk_rails_d8144e7823 FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: trade_hubs fk_rails_de9c2e1092; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade_hubs
    ADD CONSTRAINT fk_rails_de9c2e1092 FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: public_trade_orders fk_rails_e569498e2e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_trade_orders
    ADD CONSTRAINT fk_rails_e569498e2e FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: sales_finals fk_rails_e934079200; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_finals
    ADD CONSTRAINT fk_rails_e934079200 FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: buy_orders_analytics fk_rails_e970106908; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.buy_orders_analytics
    ADD CONSTRAINT fk_rails_e970106908 FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: station_details fk_rails_ec21522142; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_details
    ADD CONSTRAINT fk_rails_ec21522142 FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- Name: weekly_price_details fk_rails_f79d9ebdfb; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.weekly_price_details
    ADD CONSTRAINT fk_rails_f79d9ebdfb FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: public_trade_orders fk_rails_f82053a998; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.public_trade_orders
    ADD CONSTRAINT fk_rails_f82053a998 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- PostgreSQL database dump complete
--

SET search_path TO "$user", public;

INSERT INTO "schema_migrations" (version) VALUES
('20150408144002'),
('20150410082132'),
('20150413124013'),
('20150414095303'),
('20150415020059'),
('20150416154256'),
('20150417124636'),
('20150417125815'),
('20150417135716'),
('20150418073522'),
('20150418073708'),
('20150418073748'),
('20150418073936'),
('20150418075448'),
('20150418082948'),
('20150418101147'),
('20150418135311'),
('20150418135846'),
('20150419154750'),
('20150420030231'),
('20150421081357'),
('20150421082146'),
('20150421133638'),
('20150422142317'),
('20150423083440'),
('20150424082441'),
('20150517121520'),
('20150517123827'),
('20150810084729'),
('20150811084239'),
('20150811133912'),
('20150815033941'),
('20150815034519'),
('20150815133043'),
('20150815133222'),
('20150815133246'),
('20150906161346'),
('20150906171550'),
('20150909162142'),
('20150910074544'),
('20150910080646'),
('20150911080030'),
('20150913092820'),
('20150916011814'),
('20150916044407'),
('20150916051614'),
('20150916052729'),
('20151002143250'),
('20151009152532'),
('20151120100321'),
('20151126154339'),
('20160107150141'),
('20160127082642'),
('20160216021331'),
('20160216195833'),
('20160216201325'),
('20160217105428'),
('20160303141811'),
('20160405080556'),
('20160405090537'),
('20160527091718'),
('20160703142622'),
('20160707154456'),
('20160707154715'),
('20160710164656'),
('20160710164657'),
('20160725094658'),
('20160803143148'),
('20160806121730'),
('20160807163944'),
('20160808123615'),
('20160808124419'),
('20160808124908'),
('20160808152728'),
('20160810133553'),
('20160818184430'),
('20180423091840'),
('20180423095201'),
('20180423101233'),
('20180423114241'),
('20180426084227'),
('20180511123016'),
('20180512071913'),
('20180512094054'),
('20180513100414'),
('20180514091955'),
('20180515081925'),
('20180516152332'),
('20180525083418'),
('20180525084116'),
('20180525095642'),
('20180605053333'),
('20180609180253'),
('20180609181309'),
('20180610043002'),
('20180610061106'),
('20180610120052'),
('20180611101819'),
('20180612222810'),
('20180613072429'),
('20180613114613'),
('20180613154002'),
('20180615075822'),
('20180615101807'),
('20180615165310'),
('20180616194808'),
('20180618055421'),
('20180618071716'),
('20180618111154'),
('20180618112529'),
('20180619162636'),
('20180620060308'),
('20180622094812'),
('20180623042127'),
('20180623132533'),
('20180623140601'),
('20180624124026'),
('20180625131458'),
('20180626104714'),
('20180627091145'),
('20180627101339'),
('20180627102242'),
('20180627102847'),
('20180627112149'),
('20180627112208'),
('20180627115949'),
('20180627133905'),
('20180628095113'),
('20180628141624'),
('20180709155406'),
('20180709160644'),
('20180711141441'),
('20180712055505'),
('20180712075657'),
('20180713065950'),
('20180713081344'),
('20180713090331'),
('20180713092921'),
('20180713103258'),
('20180713115657'),
('20180714090426'),
('20180714120042'),
('20180714150836'),
('20180714151539'),
('20180716163335'),
('20180717071529'),
('20180717172014'),
('20180718060149'),
('20180718083636'),
('20180718093413'),
('20180718102843'),
('20180718112214'),
('20180719075523'),
('20180719075756'),
('20180720134043'),
('20180724093847'),
('20180724181213'),
('20180725083125'),
('20180727144320'),
('20180728063218'),
('20180728070253'),
('20180728080318'),
('20180728135542'),
('20180728153458'),
('20180802103400'),
('20180802103855'),
('20180815093119'),
('20180815094036'),
('20180815140039'),
('20180816165159'),
('20180817092520'),
('20180817093521'),
('20180822094022'),
('20180822104400'),
('20180822110028'),
('20180822165603'),
('20180823092423'),
('20180823140710'),
('20180823141927'),
('20180824065727'),
('20180824093831'),
('20180828060637'),
('20180828090606'),
('20180902090458'),
('20180902114156'),
('20180902114405'),
('20180903133836'),
('20180904063731'),
('20180904064749'),
('20180904065442'),
('20180905130609'),
('20180906131140'),
('20180907080824'),
('20180907112602'),
('20180907113512'),
('20180907121823'),
('20180907124531'),
('20180907131230'),
('20180907131346'),
('20180907160310'),
('20180912001820'),
('20180912002109'),
('20180912112146'),
('20180913131039'),
('20180913141720'),
('20180915020116'),
('20180915021818'),
('20180920082908'),
('20180926124854'),
('20180927070849'),
('20181001064444'),
('20181001093144'),
('20181002082626'),
('20181002131805'),
('20181003075233'),
('20181005093510'),
('20181005103327'),
('20181008013156'),
('20181008070647'),
('20181008071507'),
('20181106054636'),
('20181106072050');



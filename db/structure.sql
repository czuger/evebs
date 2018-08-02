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
-- Name: blueprint_component_sales_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blueprint_component_sales_orders (
    id bigint NOT NULL,
    trade_hub_id bigint NOT NULL,
    blueprint_component_id bigint NOT NULL,
    cpp_order_id bigint NOT NULL,
    volume bigint NOT NULL,
    price double precision NOT NULL,
    touched boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: blueprint_component_sales_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.blueprint_component_sales_orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: blueprint_component_sales_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.blueprint_component_sales_orders_id_seq OWNED BY public.blueprint_component_sales_orders.id;


--
-- Name: blueprint_components; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blueprint_components (
    id integer NOT NULL,
    cpp_eve_item_id integer NOT NULL,
    name character varying NOT NULL,
    cost double precision,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    volume double precision NOT NULL
);


--
-- Name: blueprint_materials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blueprint_materials (
    id integer NOT NULL,
    blueprint_id integer NOT NULL,
    blueprint_component_id integer NOT NULL,
    required_qtt integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
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
    blueprint_component_id bigint NOT NULL,
    station_detail_id bigint,
    quantity bigint NOT NULL,
    touched boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    user_id bigint NOT NULL
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
-- Name: bpc_jita_sales_finals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bpc_jita_sales_finals (
    id bigint NOT NULL,
    blueprint_component_id bigint,
    volume bigint NOT NULL,
    price double precision NOT NULL,
    cpp_order_id bigint NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: bpc_jita_sales_finals_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bpc_jita_sales_finals_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bpc_jita_sales_finals_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bpc_jita_sales_finals_id_seq OWNED BY public.bpc_jita_sales_finals.id;


--
-- Name: bpc_prices_mins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bpc_prices_mins (
    id bigint NOT NULL,
    trade_hub_id bigint NOT NULL,
    blueprint_component_id bigint NOT NULL,
    volume bigint,
    price double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: bpc_prices_mins_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bpc_prices_mins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bpc_prices_mins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bpc_prices_mins_id_seq OWNED BY public.bpc_prices_mins.id;


--
-- Name: component_to_buys; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.component_to_buys AS
SELECT
    NULL::integer AS id,
    NULL::integer AS user_id,
    NULL::character varying AS name,
    NULL::double precision AS qtt_to_buy,
    NULL::double precision AS total_cost;


--
-- Name: components_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.components_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: components_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.components_id_seq OWNED BY public.blueprint_components.id;


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
    blueprint_id bigint NOT NULL
);


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
-- Name: eve_items_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.eve_items_users (
    id integer NOT NULL,
    user_id integer,
    eve_item_id integer
);


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
-- Name: jita_margins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jita_margins (
    id integer NOT NULL,
    eve_item_id integer,
    margin double precision,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    margin_percent double precision,
    jita_min_price double precision,
    cost double precision,
    mens_volume bigint DEFAULT 0 NOT NULL,
    batch_size bigint DEFAULT 0 NOT NULL
);


--
-- Name: jita_margins_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.jita_margins_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: jita_margins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.jita_margins_id_seq OWNED BY public.jita_margins.id;


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
    region_id integer,
    vol_month bigint,
    vol_day bigint,
    cost double precision,
    min_price double precision,
    avg_price double precision,
    daily_monthly_pcent real,
    full_batch_size integer,
    prod_qtt integer,
    single_unit_cost double precision,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    margin_percent double precision,
    price_avg_week double precision,
    history_volume bigint
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
    user_pl_share_id bigint,
    download_orders_running boolean DEFAULT false NOT NULL,
    last_orders_download timestamp without time zone
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
    prices_advices_sub_1.history_volume,
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
            pa.single_unit_cost,
            pa.min_price,
            pa.price_avg_week,
            pa.vol_month,
            pa.history_volume,
            pa.full_batch_size,
            pa.daily_monthly_pcent,
            pa.margin_percent,
                CASE
                    WHEN ur.batch_cap THEN LEAST((pa.full_batch_size)::numeric, floor((((pa.history_volume * ur.vol_month_pcent))::numeric * 0.01)))
                    ELSE floor((((pa.history_volume * ur.vol_month_pcent))::numeric * 0.01))
                END AS batch_size_formula,
            ur.min_amount_for_advice,
            ur.min_pcent_for_advice
           FROM ((((((public.prices_advices pa
             JOIN public.eve_items ei ON ((pa.eve_item_id = ei.id)))
             JOIN public.trade_hubs tu ON ((pa.trade_hub_id = tu.id)))
             JOIN public.regions re ON ((re.id = tu.region_id)))
             JOIN public.trade_hubs_users thu ON ((thu.trade_hub_id = pa.trade_hub_id)))
             JOIN public.eve_items_users eiu ON ((eiu.eve_item_id = pa.eve_item_id)))
             JOIN public.users ur ON ((thu.user_id = ur.id)))
          WHERE ((pa.history_volume IS NOT NULL) AND (ur.id = eiu.user_id))) prices_advices_sub_1;


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
-- Name: production_list_share_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.production_list_share_requests (
    id bigint NOT NULL,
    sender_id bigint NOT NULL,
    recipient_id bigint NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: production_list_share_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.production_list_share_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: production_list_share_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.production_list_share_requests_id_seq OWNED BY public.production_list_share_requests.id;


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
    quantity_to_produce bigint,
    runs_count bigint
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
-- Name: sales_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sales_orders (
    id bigint NOT NULL,
    day date NOT NULL,
    volume bigint NOT NULL,
    price double precision NOT NULL,
    order_id bigint NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    trade_hub_id bigint NOT NULL,
    eve_item_id bigint NOT NULL,
    duration integer,
    touched boolean DEFAULT false NOT NULL,
    issued timestamp without time zone,
    end_time timestamp without time zone
);


--
-- Name: sales_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sales_orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sales_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sales_orders_id_seq OWNED BY public.sales_orders.id;


--
-- Name: sales_orders_process_infos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sales_orders_process_infos (
    id bigint NOT NULL,
    key character varying NOT NULL,
    last_retrieve_session_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: sales_orders_process_infos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sales_orders_process_infos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sales_orders_process_infos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sales_orders_process_infos_id_seq OWNED BY public.sales_orders_process_infos.id;


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
-- Name: type_in_regions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.type_in_regions (
    id bigint NOT NULL,
    cpp_region_id integer NOT NULL,
    cpp_type_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: type_in_regions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.type_in_regions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: type_in_regions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.type_in_regions_id_seq OWNED BY public.type_in_regions.id;


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
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    price double precision
);


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
-- Name: blueprint_component_sales_orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_component_sales_orders ALTER COLUMN id SET DEFAULT nextval('public.blueprint_component_sales_orders_id_seq'::regclass);


--
-- Name: blueprint_components id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_components ALTER COLUMN id SET DEFAULT nextval('public.components_id_seq'::regclass);


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
-- Name: bpc_jita_sales_finals id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_jita_sales_finals ALTER COLUMN id SET DEFAULT nextval('public.bpc_jita_sales_finals_id_seq'::regclass);


--
-- Name: bpc_prices_mins id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_prices_mins ALTER COLUMN id SET DEFAULT nextval('public.bpc_prices_mins_id_seq'::regclass);


--
-- Name: crontabs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.crontabs ALTER COLUMN id SET DEFAULT nextval('public.crontabs_id_seq'::regclass);


--
-- Name: eve_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items ALTER COLUMN id SET DEFAULT nextval('public.eve_items_id_seq'::regclass);


--
-- Name: eve_items_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items_users ALTER COLUMN id SET DEFAULT nextval('public.eve_items_users_id_seq'::regclass);


--
-- Name: identities id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.identities ALTER COLUMN id SET DEFAULT nextval('public.identities_id_seq'::regclass);


--
-- Name: jita_margins id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jita_margins ALTER COLUMN id SET DEFAULT nextval('public.jita_margins_id_seq'::regclass);


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
-- Name: production_list_share_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_list_share_requests ALTER COLUMN id SET DEFAULT nextval('public.production_list_share_requests_id_seq'::regclass);


--
-- Name: production_lists id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_lists ALTER COLUMN id SET DEFAULT nextval('public.production_lists_id_seq'::regclass);


--
-- Name: regions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.regions ALTER COLUMN id SET DEFAULT nextval('public.regions_id_seq'::regclass);


--
-- Name: sales_finals id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_finals ALTER COLUMN id SET DEFAULT nextval('public.sales_finals_id_seq'::regclass);


--
-- Name: sales_orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders ALTER COLUMN id SET DEFAULT nextval('public.sales_orders_id_seq'::regclass);


--
-- Name: sales_orders_process_infos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders_process_infos ALTER COLUMN id SET DEFAULT nextval('public.sales_orders_process_infos_id_seq'::regclass);


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
-- Name: type_in_regions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.type_in_regions ALTER COLUMN id SET DEFAULT nextval('public.type_in_regions_id_seq'::regclass);


--
-- Name: user_activity_logs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_activity_logs ALTER COLUMN id SET DEFAULT nextval('public.user_activity_logs_id_seq'::regclass);


--
-- Name: user_sale_orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_sale_orders ALTER COLUMN id SET DEFAULT nextval('public.user_sale_orders_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: ar_internal_metadata ar_internal_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ar_internal_metadata
    ADD CONSTRAINT ar_internal_metadata_pkey PRIMARY KEY (key);


--
-- Name: blueprint_component_sales_orders blueprint_component_sales_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_component_sales_orders
    ADD CONSTRAINT blueprint_component_sales_orders_pkey PRIMARY KEY (id);


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
-- Name: bpc_jita_sales_finals bpc_jita_sales_finals_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_jita_sales_finals
    ADD CONSTRAINT bpc_jita_sales_finals_pkey PRIMARY KEY (id);


--
-- Name: bpc_prices_mins bpc_prices_mins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_prices_mins
    ADD CONSTRAINT bpc_prices_mins_pkey PRIMARY KEY (id);


--
-- Name: blueprint_components compenents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_components
    ADD CONSTRAINT compenents_pkey PRIMARY KEY (id);


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
-- Name: eve_items_users eve_items_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.eve_items_users
    ADD CONSTRAINT eve_items_users_pkey PRIMARY KEY (id);


--
-- Name: identities identities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.identities
    ADD CONSTRAINT identities_pkey PRIMARY KEY (id);


--
-- Name: jita_margins jita_margins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jita_margins
    ADD CONSTRAINT jita_margins_pkey PRIMARY KEY (id);


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
-- Name: production_list_share_requests production_list_share_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_list_share_requests
    ADD CONSTRAINT production_list_share_requests_pkey PRIMARY KEY (id);


--
-- Name: production_lists production_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_lists
    ADD CONSTRAINT production_lists_pkey PRIMARY KEY (id);


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
-- Name: sales_orders sales_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_pkey PRIMARY KEY (id);


--
-- Name: sales_orders_process_infos sales_orders_process_infos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders_process_infos
    ADD CONSTRAINT sales_orders_process_infos_pkey PRIMARY KEY (id);


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
-- Name: type_in_regions type_in_regions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.type_in_regions
    ADD CONSTRAINT type_in_regions_pkey PRIMARY KEY (id);


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
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: index_bcso_blueprint_component; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bcso_blueprint_component ON public.blueprint_component_sales_orders USING btree (blueprint_component_id);


--
-- Name: index_blueprint_component_sales_orders_on_cpp_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_blueprint_component_sales_orders_on_cpp_order_id ON public.blueprint_component_sales_orders USING btree (cpp_order_id);


--
-- Name: index_blueprint_component_sales_orders_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_blueprint_component_sales_orders_on_trade_hub_id ON public.blueprint_component_sales_orders USING btree (trade_hub_id);


--
-- Name: index_blueprint_components_on_cpp_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_blueprint_components_on_cpp_eve_item_id ON public.blueprint_components USING btree (cpp_eve_item_id);


--
-- Name: index_blueprint_components_on_lower_name; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_blueprint_components_on_lower_name ON public.blueprint_components USING btree (lower((name)::text));


--
-- Name: index_blueprint_materials_on_blueprint_component_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_blueprint_materials_on_blueprint_component_id ON public.blueprint_materials USING btree (blueprint_component_id);


--
-- Name: index_blueprint_materials_on_blueprint_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_blueprint_materials_on_blueprint_id ON public.blueprint_materials USING btree (blueprint_id);


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
-- Name: index_bpc_assets_on_blueprint_component_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_assets_on_blueprint_component_id ON public.bpc_assets USING btree (blueprint_component_id);


--
-- Name: index_bpc_assets_on_station_detail_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_assets_on_station_detail_id ON public.bpc_assets USING btree (station_detail_id);


--
-- Name: index_bpc_jita_sales_finals_on_blueprint_component_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_jita_sales_finals_on_blueprint_component_id ON public.bpc_jita_sales_finals USING btree (blueprint_component_id);


--
-- Name: index_bpc_prices_mins_on_blueprint_component_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_prices_mins_on_blueprint_component_id ON public.bpc_prices_mins USING btree (blueprint_component_id);


--
-- Name: index_bpc_prices_mins_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_bpc_prices_mins_on_trade_hub_id ON public.bpc_prices_mins USING btree (trade_hub_id);


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
-- Name: index_eve_items_users_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_items_users_on_eve_item_id ON public.eve_items_users USING btree (eve_item_id);


--
-- Name: index_eve_items_users_on_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_eve_items_users_on_user_id ON public.eve_items_users USING btree (user_id);


--
-- Name: index_jita_margins_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_jita_margins_on_eve_item_id ON public.jita_margins USING btree (eve_item_id);


--
-- Name: index_market_groups_on_cpp_market_group_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_market_groups_on_cpp_market_group_id ON public.market_groups USING btree (cpp_market_group_id);


--
-- Name: index_prices_advices_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_prices_advices_on_eve_item_id ON public.prices_advices USING btree (eve_item_id);


--
-- Name: index_prices_advices_on_margin_percent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_prices_advices_on_margin_percent ON public.prices_advices USING btree (margin_percent);


--
-- Name: index_prices_advices_on_region_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_prices_advices_on_region_id ON public.prices_advices USING btree (region_id);


--
-- Name: index_prices_advices_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_prices_advices_on_trade_hub_id ON public.prices_advices USING btree (trade_hub_id);


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
-- Name: index_sales_orders_on_eve_item_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_sales_orders_on_eve_item_id ON public.sales_orders USING btree (eve_item_id);


--
-- Name: index_sales_orders_on_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX index_sales_orders_on_order_id ON public.sales_orders USING btree (order_id);


--
-- Name: index_sales_orders_on_trade_hub_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_sales_orders_on_trade_hub_id ON public.sales_orders USING btree (trade_hub_id);


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
-- Name: index_type_in_regions_on_cpp_region_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX index_type_in_regions_on_cpp_region_id ON public.type_in_regions USING btree (cpp_region_id);


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
-- Name: market_group_anc_desc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX market_group_anc_desc_idx ON public.market_group_hierarchies USING btree (ancestor_id, descendant_id, generations);


--
-- Name: market_group_desc_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX market_group_desc_idx ON public.market_group_hierarchies USING btree (descendant_id);


--
-- Name: plsr_unique_index; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX plsr_unique_index ON public.production_list_share_requests USING btree (recipient_id, sender_id);


--
-- Name: unique_schema_migrations; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX unique_schema_migrations ON public.schema_migrations USING btree (version);


--
-- Name: component_to_buys _RETURN; Type: RULE; Schema: public; Owner: -
--

CREATE OR REPLACE VIEW public.component_to_buys AS
 SELECT bc.id,
    pl.user_id,
    bc.name,
    (sum((ceil(((bm.required_qtt)::double precision * COALESCE(bmo.percent_modification_value, (1)::double precision))) * (pl.runs_count)::double precision)) - (COALESCE(ba.quantity, (0)::bigint))::double precision) AS qtt_to_buy,
    ((sum((ceil(((bm.required_qtt)::double precision * COALESCE(bmo.percent_modification_value, (1)::double precision))) * (pl.runs_count)::double precision)) - (COALESCE(ba.quantity, (0)::bigint))::double precision) * bc.cost) AS total_cost
   FROM ((((((public.production_lists pl
     JOIN public.eve_items ei ON ((ei.id = pl.eve_item_id)))
     JOIN public.blueprints b ON ((ei.blueprint_id = b.id)))
     JOIN public.blueprint_materials bm ON ((b.id = bm.blueprint_id)))
     JOIN public.blueprint_components bc ON ((bm.blueprint_component_id = bc.id)))
     LEFT JOIN public.blueprint_modifications bmo ON (((b.id = bmo.blueprint_id) AND (bmo.user_id = pl.user_id))))
     LEFT JOIN public.bpc_assets ba ON ((bc.id = ba.blueprint_component_id)))
  WHERE (pl.runs_count IS NOT NULL)
  GROUP BY bc.id, pl.user_id, bc.name, COALESCE(ba.quantity, (0)::bigint)
 HAVING ((sum((ceil(((bm.required_qtt)::double precision * COALESCE(bmo.percent_modification_value, (1)::double precision))) * (pl.runs_count)::double precision)) - (COALESCE(ba.quantity, (0)::bigint))::double precision) > (0)::double precision);


--
-- Name: production_lists fk_rails_0a4a7e08c4; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_lists
    ADD CONSTRAINT fk_rails_0a4a7e08c4 FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: prices_advices fk_rails_0c863bd6cb; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_advices
    ADD CONSTRAINT fk_rails_0c863bd6cb FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: blueprint_component_sales_orders fk_rails_0e91d4accb; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_component_sales_orders
    ADD CONSTRAINT fk_rails_0e91d4accb FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


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
-- Name: structures fk_rails_38f8c90abc; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.structures
    ADD CONSTRAINT fk_rails_38f8c90abc FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: bpc_assets fk_rails_46a1eaaaca; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_assets
    ADD CONSTRAINT fk_rails_46a1eaaaca FOREIGN KEY (blueprint_component_id) REFERENCES public.blueprint_components(id);


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
-- Name: bpc_prices_mins fk_rails_7537628695; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_prices_mins
    ADD CONSTRAINT fk_rails_7537628695 FOREIGN KEY (blueprint_component_id) REFERENCES public.blueprint_components(id);


--
-- Name: blueprint_modifications fk_rails_7744def0ba; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_modifications
    ADD CONSTRAINT fk_rails_7744def0ba FOREIGN KEY (blueprint_id) REFERENCES public.blueprints(id);


--
-- Name: production_list_share_requests fk_rails_844f9d0f43; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_list_share_requests
    ADD CONSTRAINT fk_rails_844f9d0f43 FOREIGN KEY (recipient_id) REFERENCES public.users(id);


--
-- Name: sales_orders fk_rails_86221bcddd; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT fk_rails_86221bcddd FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: sales_finals fk_rails_8d037fe800; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_finals
    ADD CONSTRAINT fk_rails_8d037fe800 FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: bpc_prices_mins fk_rails_b0d0314be6; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_prices_mins
    ADD CONSTRAINT fk_rails_b0d0314be6 FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: prices_advices fk_rails_b6b5f49d4d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_advices
    ADD CONSTRAINT fk_rails_b6b5f49d4d FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: production_list_share_requests fk_rails_c7348cfe3d; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.production_list_share_requests
    ADD CONSTRAINT fk_rails_c7348cfe3d FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- Name: sales_orders fk_rails_c9b4527c2e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT fk_rails_c9b4527c2e FOREIGN KEY (eve_item_id) REFERENCES public.eve_items(id);


--
-- Name: prices_advices fk_rails_ccdf67e46e; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices_advices
    ADD CONSTRAINT fk_rails_ccdf67e46e FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: trade_hubs fk_rails_de9c2e1092; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade_hubs
    ADD CONSTRAINT fk_rails_de9c2e1092 FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: sales_finals fk_rails_e934079200; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_finals
    ADD CONSTRAINT fk_rails_e934079200 FOREIGN KEY (trade_hub_id) REFERENCES public.trade_hubs(id);


--
-- Name: station_details fk_rails_ec21522142; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_details
    ADD CONSTRAINT fk_rails_ec21522142 FOREIGN KEY (station_id) REFERENCES public.stations(id);


--
-- Name: users fk_rails_f3391600f4; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_rails_f3391600f4 FOREIGN KEY (user_pl_share_id) REFERENCES public.users(id);


--
-- Name: bpc_jita_sales_finals fk_rails_f68bf0beb4; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bpc_jita_sales_finals
    ADD CONSTRAINT fk_rails_f68bf0beb4 FOREIGN KEY (blueprint_component_id) REFERENCES public.blueprint_components(id);


--
-- Name: blueprint_component_sales_orders fk_rails_f729252d04; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_component_sales_orders
    ADD CONSTRAINT fk_rails_f729252d04 FOREIGN KEY (blueprint_component_id) REFERENCES public.blueprint_components(id);


--
-- Name: blueprint_materials fk_rails_f8f740aa48; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.blueprint_materials
    ADD CONSTRAINT fk_rails_f8f740aa48 FOREIGN KEY (blueprint_component_id) REFERENCES public.blueprint_components(id);


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
('20180802103400');



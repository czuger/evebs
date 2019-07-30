# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 2019_07_30_062459) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "blueprint_materials", id: :serial, force: :cascade do |t|
    t.integer "blueprint_id", null: false
    t.integer "required_qtt", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "eve_item_id", null: false
    t.index ["blueprint_id"], name: "index_blueprint_materials_on_blueprint_id"
    t.index ["eve_item_id"], name: "index_blueprint_materials_on_eve_item_id"
  end

  create_table "blueprint_modifications", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.bigint "blueprint_id", null: false
    t.float "percent_modification_value", null: false
    t.boolean "touched", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id", "blueprint_id"], name: "index_blueprint_modifications_on_user_id_and_blueprint_id", unique: true
  end

  create_table "blueprints", id: :serial, force: :cascade do |t|
    t.integer "produced_cpp_type_id", null: false
    t.integer "nb_runs", null: false
    t.integer "prod_qtt", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "cpp_blueprint_id", null: false
    t.string "name", null: false
    t.index ["cpp_blueprint_id"], name: "index_blueprints_on_cpp_blueprint_id", unique: true
    t.index ["produced_cpp_type_id"], name: "index_blueprints_on_produced_cpp_type_id", unique: true
  end

  create_table "bpc_assets", force: :cascade do |t|
    t.bigint "universe_station_id"
    t.bigint "quantity", null: false
    t.boolean "touched", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.bigint "eve_item_id", null: false
    t.index ["eve_item_id"], name: "index_bpc_assets_on_eve_item_id"
    t.index ["universe_station_id"], name: "index_bpc_assets_on_universe_station_id"
  end

  create_table "bpc_assets_stations", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.bigint "universe_station_id", null: false
    t.boolean "touched", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["universe_station_id"], name: "index_bpc_assets_stations_on_universe_station_id"
    t.index ["user_id"], name: "index_bpc_assets_stations_on_user_id"
  end

  create_table "buy_orders_analytics", force: :cascade do |t|
    t.bigint "trade_hub_id", null: false
    t.bigint "eve_item_id", null: false
    t.float "approx_max_price"
    t.bigint "over_approx_max_price_volume"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.float "single_unit_cost"
    t.float "single_unit_margin"
    t.float "estimated_volume_margin"
    t.float "per_job_margin"
    t.float "per_job_run_margin"
    t.float "final_margin"
    t.index ["eve_item_id", "trade_hub_id"], name: "index_buy_orders_analytics_on_eve_item_id_and_trade_hub_id", unique: true
  end

  create_table "crontabs", force: :cascade do |t|
    t.string "cron_name", null: false
    t.boolean "status", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "eve_items", id: :serial, force: :cascade do |t|
    t.integer "cpp_eve_item_id", null: false
    t.string "name", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.float "cost"
    t.integer "market_group_id"
    t.bigint "blueprint_id"
    t.float "volume"
    t.integer "production_level", default: 0, null: false
    t.boolean "base_item", default: false, null: false
    t.float "cpp_market_adjusted_price"
    t.float "cpp_market_average_price"
    t.string "description"
    t.json "market_group_path", default: [], null: false
    t.float "mass"
    t.float "packaged_volume"
    t.float "weekly_avg_price"
    t.boolean "faction", default: false, null: false
    t.index "lower((name)::text)", name: "index_eve_items_on_lower_name", unique: true
    t.index ["blueprint_id"], name: "index_eve_items_on_blueprint_id"
    t.index ["cpp_eve_item_id"], name: "index_eve_items_on_cpp_eve_item_id"
    t.index ["market_group_id"], name: "index_eve_items_on_market_group_id"
  end

  create_table "eve_items_saved_lists", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "description", null: false
    t.string "saved_ids", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_eve_items_saved_lists_on_user_id"
  end

  create_table "eve_items_users", id: :serial, force: :cascade do |t|
    t.integer "user_id"
    t.integer "eve_item_id"
    t.index ["eve_item_id"], name: "index_eve_items_users_on_eve_item_id"
    t.index ["user_id"], name: "index_eve_items_users_on_user_id"
  end

  create_table "eve_market_histories", force: :cascade do |t|
    t.bigint "region_id", null: false
    t.bigint "eve_item_id", null: false
    t.bigint "volume", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.float "highest"
    t.float "lowest"
    t.float "average"
    t.bigint "order_count"
    t.date "server_date"
    t.index ["eve_item_id"], name: "index_eve_market_histories_on_eve_item_id"
    t.index ["region_id"], name: "index_eve_market_histories_on_region_id"
  end

  create_table "identities", id: :serial, force: :cascade do |t|
    t.string "name"
    t.string "email"
    t.string "password_digest"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "last_updates", force: :cascade do |t|
    t.string "update_type", null: false
    t.datetime "updated_at", null: false
  end

  create_table "market_group_hierarchies", id: false, force: :cascade do |t|
    t.integer "ancestor_id", null: false
    t.integer "descendant_id", null: false
    t.integer "generations", null: false
    t.index ["ancestor_id", "descendant_id", "generations"], name: "market_group_anc_desc_idx", unique: true
    t.index ["descendant_id"], name: "market_group_desc_idx"
  end

  create_table "market_groups", id: :serial, force: :cascade do |t|
    t.string "name", null: false
    t.integer "parent_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "cpp_market_group_id", null: false
    t.integer "cpp_parent_market_group_id"
    t.index ["cpp_market_group_id"], name: "index_market_groups_on_cpp_market_group_id", unique: true
  end

  create_table "prices_advices", id: :serial, force: :cascade do |t|
    t.integer "eve_item_id", null: false
    t.integer "trade_hub_id", null: false
    t.bigint "vol_month"
    t.float "avg_price_month"
    t.float "immediate_montly_pcent"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.float "margin_percent"
    t.float "avg_price_week"
    t.index ["eve_item_id", "trade_hub_id"], name: "index_prices_advices_on_eve_item_id_and_trade_hub_id", unique: true
    t.index ["margin_percent"], name: "index_prices_advices_on_margin_percent"
  end

  create_table "prices_mins", id: :serial, force: :cascade do |t|
    t.integer "eve_item_id"
    t.integer "trade_hub_id"
    t.float "min_price"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.bigint "volume"
    t.index ["eve_item_id", "trade_hub_id"], name: "index_prices_mins_on_eve_item_id_and_trade_hub_id", unique: true
  end

  create_table "production_lists", id: :serial, force: :cascade do |t|
    t.integer "user_id", null: false
    t.integer "trade_hub_id", null: false
    t.integer "eve_item_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "runs_count", limit: 2
    t.index ["eve_item_id"], name: "index_production_lists_on_eve_item_id"
    t.index ["trade_hub_id"], name: "index_production_lists_on_trade_hub_id"
    t.index ["user_id"], name: "index_production_lists_on_user_id"
  end

  create_table "public_trade_orders", force: :cascade do |t|
    t.bigint "trade_hub_id", null: false
    t.bigint "eve_item_id", null: false
    t.bigint "order_id", null: false
    t.boolean "is_buy_order", null: false
    t.datetime "end_time", null: false
    t.float "price", null: false
    t.string "range", null: false
    t.bigint "volume_remain", null: false
    t.bigint "volume_total", null: false
    t.bigint "min_volume", null: false
    t.boolean "touched", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["eve_item_id"], name: "index_public_trade_orders_on_eve_item_id"
    t.index ["order_id"], name: "index_public_trade_orders_on_order_id", unique: true
    t.index ["trade_hub_id"], name: "index_public_trade_orders_on_trade_hub_id"
  end

  create_table "regions", id: :serial, force: :cascade do |t|
    t.string "cpp_region_id", null: false
    t.string "name", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.integer "orders_pages_count", default: 0, null: false
    t.index ["cpp_region_id"], name: "index_regions_on_cpp_region_id", unique: true
  end

  create_table "sales_finals", force: :cascade do |t|
    t.date "day", null: false
    t.bigint "trade_hub_id", null: false
    t.bigint "eve_item_id", null: false
    t.bigint "volume", null: false
    t.float "price", null: false
    t.bigint "order_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["eve_item_id"], name: "index_sales_finals_on_eve_item_id"
    t.index ["trade_hub_id"], name: "index_sales_finals_on_trade_hub_id"
  end

  create_table "stations", id: :serial, force: :cascade do |t|
    t.integer "trade_hub_id"
    t.string "name"
    t.integer "cpp_station_id"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.index ["cpp_station_id"], name: "index_stations_on_cpp_station_id"
    t.index ["trade_hub_id"], name: "index_stations_on_trade_hub_id"
  end

  create_table "structures", force: :cascade do |t|
    t.bigint "cpp_structure_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.boolean "forbidden", default: true, null: false
    t.bigint "universe_system_id"
    t.integer "orders_count_pages"
    t.index ["cpp_structure_id"], name: "index_structures_on_cpp_structure_id", unique: true
    t.index ["forbidden"], name: "index_structures_on_forbidden"
    t.index ["universe_system_id"], name: "index_structures_on_universe_system_id"
  end

  create_table "trade_hubs", id: :serial, force: :cascade do |t|
    t.integer "eve_system_id", null: false
    t.string "name", null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer "region_id"
    t.boolean "inner", default: false, null: false
    t.index ["eve_system_id"], name: "index_trade_hubs_on_eve_system_id", unique: true
    t.index ["region_id"], name: "index_trade_hubs_on_region_id"
  end

  create_table "trade_hubs_users", id: :serial, force: :cascade do |t|
    t.integer "user_id"
    t.integer "trade_hub_id"
    t.index ["trade_hub_id"], name: "index_trade_hubs_users_on_trade_hub_id"
    t.index ["user_id"], name: "index_trade_hubs_users_on_user_id"
  end

  create_table "trade_volume_estimations", force: :cascade do |t|
    t.bigint "universe_station_id"
    t.bigint "eve_item_id"
    t.string "day_timestamp", null: false
    t.bigint "volume_total_sum", default: 0, null: false
    t.float "volume_percent", default: 0.0, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "orders", default: [], null: false, array: true
    t.index ["universe_station_id", "eve_item_id"], name: "index_trade_volume_estimations_on_us_id_and_eve_item_id", unique: true
  end

  create_table "universe_stations", force: :cascade do |t|
    t.integer "cpp_system_id", null: false
    t.integer "cpp_station_id", null: false
    t.string "name", null: false
    t.string "services", null: false, array: true
    t.float "office_rental_cost", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "station_id"
    t.float "security_status"
    t.integer "jita_distance", limit: 2
    t.jsonb "industry_costs_indices"
    t.bigint "universe_system_id", null: false
    t.index ["cpp_station_id"], name: "index_universe_stations_on_cpp_station_id", unique: true
    t.index ["station_id"], name: "index_universe_stations_on_station_id"
    t.index ["universe_system_id"], name: "index_universe_stations_on_universe_system_id"
  end

  create_table "universe_systems", force: :cascade do |t|
    t.integer "cpp_system_id", null: false
    t.string "name", null: false
    t.boolean "trade_hub", default: false, null: false
    t.integer "cpp_constellation_id", null: false
    t.integer "cpp_star_id", null: false
    t.string "security_class"
    t.float "security_status", null: false
    t.integer "stations_ids", default: [], null: false, array: true
    t.integer "kill_stats_current_month", default: 0, null: false
    t.integer "kill_stats_last_month", default: 0, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["cpp_system_id"], name: "index_universe_systems_on_cpp_system_id", unique: true
    t.index ["trade_hub"], name: "index_universe_systems_on_trade_hub"
  end

  create_table "user_activity_logs", id: :serial, force: :cascade do |t|
    t.string "ip"
    t.string "action"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "user"
  end

  create_table "user_sale_orders", id: :serial, force: :cascade do |t|
    t.integer "user_id", null: false
    t.integer "eve_item_id", null: false
    t.integer "trade_hub_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.float "price", null: false
    t.index ["eve_item_id"], name: "index_user_sale_orders_on_eve_item_id"
    t.index ["trade_hub_id"], name: "index_user_sale_orders_on_trade_hub_id"
    t.index ["user_id"], name: "index_user_sale_orders_on_user_id"
  end

  create_table "user_to_user_duplication_requests", force: :cascade do |t|
    t.integer "sender_id", null: false
    t.integer "receiver_id", null: false
    t.integer "duplication_type", limit: 2, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["receiver_id"], name: "index_user_to_user_duplication_requests_on_receiver_id"
    t.index ["sender_id"], name: "index_user_to_user_duplication_requests_on_sender_id"
  end

  create_table "users", id: :serial, force: :cascade do |t|
    t.string "name"
    t.boolean "remove_occuped_places"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string "provider"
    t.string "uid"
    t.datetime "last_changes_in_choices"
    t.integer "min_pcent_for_advice"
    t.boolean "watch_my_prices"
    t.float "min_amount_for_advice"
    t.boolean "admin", default: false, null: false
    t.boolean "batch_cap", default: true, null: false
    t.integer "vol_month_pcent", default: 10, null: false
    t.datetime "expires_on"
    t.string "token"
    t.string "renew_token"
    t.boolean "locked", default: false, null: false
    t.boolean "download_assets_running", default: false, null: false
    t.datetime "last_assets_download"
    t.boolean "download_orders_running", default: false, null: false
    t.datetime "last_orders_download"
    t.integer "batch_cap_multiplier", default: 1, null: false
    t.integer "last_duplication_receiver_id"
    t.bigint "selected_assets_station_id"
    t.boolean "download_blueprints_running", default: false, null: false
    t.datetime "last_blueprints_download"
    t.integer "sales_orders_show_margin_min"
  end

  create_table "weekly_price_details", force: :cascade do |t|
    t.bigint "eve_item_id", null: false
    t.date "day", null: false
    t.float "volume", null: false
    t.float "weighted_avg_price", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "trade_hub_id", null: false
    t.index ["eve_item_id", "trade_hub_id", "day"], name: "wpd_eve_item_id_trade_hub_id_day", unique: true
  end

  add_foreign_key "blueprint_materials", "blueprints"
  add_foreign_key "blueprint_materials", "eve_items"
  add_foreign_key "blueprint_modifications", "blueprints"
  add_foreign_key "blueprint_modifications", "users"
  add_foreign_key "bpc_assets", "eve_items"
  add_foreign_key "bpc_assets", "universe_stations"
  add_foreign_key "bpc_assets", "users"
  add_foreign_key "bpc_assets_stations", "universe_stations"
  add_foreign_key "bpc_assets_stations", "users"
  add_foreign_key "buy_orders_analytics", "eve_items"
  add_foreign_key "buy_orders_analytics", "trade_hubs"
  add_foreign_key "eve_items", "blueprints"
  add_foreign_key "eve_items", "market_groups"
  add_foreign_key "eve_items_saved_lists", "users"
  add_foreign_key "eve_market_histories", "eve_items"
  add_foreign_key "eve_market_histories", "regions"
  add_foreign_key "prices_advices", "eve_items"
  add_foreign_key "prices_advices", "trade_hubs"
  add_foreign_key "production_lists", "eve_items"
  add_foreign_key "production_lists", "trade_hubs"
  add_foreign_key "production_lists", "users"
  add_foreign_key "public_trade_orders", "eve_items"
  add_foreign_key "public_trade_orders", "trade_hubs"
  add_foreign_key "sales_finals", "eve_items"
  add_foreign_key "sales_finals", "trade_hubs"
  add_foreign_key "structures", "universe_systems"
  add_foreign_key "trade_hubs", "regions"
  add_foreign_key "trade_volume_estimations", "eve_items"
  add_foreign_key "trade_volume_estimations", "universe_stations"
  add_foreign_key "universe_stations", "stations"
  add_foreign_key "universe_stations", "universe_systems"
  add_foreign_key "user_sale_orders", "eve_items"
  add_foreign_key "user_sale_orders", "trade_hubs"
  add_foreign_key "user_sale_orders", "users"
  add_foreign_key "user_to_user_duplication_requests", "users", column: "receiver_id"
  add_foreign_key "user_to_user_duplication_requests", "users", column: "sender_id"
  add_foreign_key "users", "universe_stations", column: "selected_assets_station_id"
  add_foreign_key "weekly_price_details", "eve_items"
  add_foreign_key "weekly_price_details", "trade_hubs"

  create_view "buy_orders_analytics_results", sql_definition: <<-SQL
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
     FROM ((((((buy_orders_analytics boa
       JOIN eve_items ei ON ((ei.id = boa.eve_item_id)))
       JOIN trade_hubs tu ON ((boa.trade_hub_id = tu.id)))
       JOIN trade_hubs_users thu ON ((boa.trade_hub_id = thu.trade_hub_id)))
       JOIN eve_items_users eiu ON ((boa.eve_item_id = eiu.eve_item_id)))
       JOIN users u ON (((thu.user_id = u.id) AND (eiu.user_id = u.id))))
       JOIN regions r ON ((tu.region_id = r.id)))
    WHERE (boa.final_margin > (0)::double precision)
    ORDER BY boa.final_margin DESC;
  SQL
  create_view "price_advice_margin_comps", sql_definition: <<-SQL
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
             FROM ((((((((prices_advices pa
               JOIN eve_items ei ON ((pa.eve_item_id = ei.id)))
               JOIN blueprints bp ON ((ei.blueprint_id = bp.id)))
               JOIN trade_hubs tu ON ((pa.trade_hub_id = tu.id)))
               JOIN regions re ON ((re.id = tu.region_id)))
               JOIN trade_hubs_users thu ON ((thu.trade_hub_id = pa.trade_hub_id)))
               JOIN eve_items_users eiu ON ((eiu.eve_item_id = pa.eve_item_id)))
               JOIN users ur ON ((thu.user_id = ur.id)))
               JOIN prices_mins pm ON (((pm.trade_hub_id = pa.trade_hub_id) AND (pa.eve_item_id = pm.eve_item_id))))
            WHERE ((pa.vol_month IS NOT NULL) AND (ur.id = eiu.user_id))) prices_advices_sub_1;
  SQL
  create_view "components_to_buys", sql_definition: <<-SQL
      SELECT bpm_mat_ei.id,
      pl.user_id,
      bpm_mat_ei.name AS eve_item_name,
      bpm_mat_ei.id AS eve_item_id,
      (sum(qtt_comp.raw_qtt) - (COALESCE(ba.quantity, (0)::bigint))::double precision) AS qtt_to_buy,
      ((sum(qtt_comp.raw_qtt) - (COALESCE(ba.quantity, (0)::bigint))::double precision) * bpm_mat_ei.cost) AS total_cost,
      ((sum(qtt_comp.raw_qtt) - (COALESCE(ba.quantity, (0)::bigint))::double precision) * bpm_mat_ei.volume) AS required_volume,
      bpm_mat_ei.base_item
     FROM (((((((production_lists pl
       JOIN eve_items ei ON ((ei.id = pl.eve_item_id)))
       JOIN blueprints b ON ((ei.blueprint_id = b.id)))
       JOIN blueprint_materials bm ON ((b.id = bm.blueprint_id)))
       JOIN eve_items bpm_mat_ei ON ((bm.eve_item_id = bpm_mat_ei.id)))
       JOIN users ue ON ((pl.user_id = ue.id)))
       LEFT JOIN blueprint_modifications bmo ON (((b.id = bmo.blueprint_id) AND (bmo.user_id = pl.user_id))))
       LEFT JOIN bpc_assets ba ON (((bpm_mat_ei.id = ba.eve_item_id) AND (ba.universe_station_id = ue.selected_assets_station_id)))),
      LATERAL ( SELECT ceil((((bm.required_qtt * pl.runs_count))::double precision * COALESCE(bmo.percent_modification_value, (1)::double precision))) AS raw_qtt) qtt_comp
    WHERE (pl.runs_count > 0)
    GROUP BY bpm_mat_ei.id, pl.user_id, bpm_mat_ei.name, COALESCE(ba.quantity, (0)::bigint)
   HAVING ((sum(qtt_comp.raw_qtt) - (COALESCE(ba.quantity, (0)::bigint))::double precision) > (0)::double precision);
  SQL
  create_view "price_advices_min_prices", sql_definition: <<-SQL
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
          CASE
              WHEN (ei.cost = 'Infinity'::double precision) THEN 'Infinity'::double precision
              ELSE ((pa.avg_price_month / ei.cost) - (1)::double precision)
          END AS avg_monthly_margin_percent
     FROM (((((prices_advices pa
       JOIN eve_items ei ON ((pa.eve_item_id = ei.id)))
       JOIN blueprints bp ON ((ei.blueprint_id = bp.id)))
       JOIN trade_hubs tu ON ((pa.trade_hub_id = tu.id)))
       JOIN regions re ON ((re.id = tu.region_id)))
       LEFT JOIN prices_mins pm ON (((pm.trade_hub_id = pa.trade_hub_id) AND (pa.eve_item_id = pm.eve_item_id))));
  SQL
  create_view "group_eve_market_histories", sql_definition: <<-SQL
      SELECT eve_market_histories.region_id,
      regions.name AS region_name,
      eve_market_histories.eve_item_id,
      sum(eve_market_histories.volume) AS volume,
      sum(eve_market_histories.order_count) AS orders_count,
      max(eve_market_histories.highest) AS max_price,
      min(eve_market_histories.lowest) AS min_price,
      avg(eve_market_histories.average) AS avg_price
     FROM eve_market_histories,
      regions
    WHERE (eve_market_histories.region_id = regions.id)
    GROUP BY eve_market_histories.region_id, regions.name, eve_market_histories.eve_item_id;
  SQL
  create_view "user_sale_order_details", sql_definition: <<-SQL
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
     FROM (((((user_sale_orders uso
       JOIN eve_items ei ON ((ei.id = uso.eve_item_id)))
       JOIN blueprints b ON ((ei.blueprint_id = b.id)))
       JOIN trade_hubs tu ON ((uso.trade_hub_id = tu.id)))
       JOIN regions r ON ((tu.region_id = r.id)))
       LEFT JOIN prices_mins pm ON (((pm.eve_item_id = uso.eve_item_id) AND (pm.trade_hub_id = uso.trade_hub_id))));
  SQL
end

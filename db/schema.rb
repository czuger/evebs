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

ActiveRecord::Schema.define(version: 2018_07_18_102843) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "hstore"
  enable_extension "plpgsql"

  create_table "blueprint_component_sales_orders", force: :cascade do |t|
    t.bigint "trade_hub_id", null: false
    t.bigint "blueprint_component_id", null: false
    t.bigint "cpp_order_id", null: false
    t.bigint "volume", null: false
    t.float "price", null: false
    t.boolean "touched", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["blueprint_component_id"], name: "index_bcso_blueprint_component"
    t.index ["cpp_order_id"], name: "index_blueprint_component_sales_orders_on_cpp_order_id", unique: true
    t.index ["trade_hub_id"], name: "index_blueprint_component_sales_orders_on_trade_hub_id"
  end

  create_table "blueprint_components", id: :integer, default: -> { "nextval('components_id_seq'::regclass)" }, force: :cascade do |t|
    t.integer "cpp_eve_item_id", null: false
    t.string "name", null: false
    t.float "cost"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index "lower((name)::text)", name: "index_blueprint_components_on_lower_name", unique: true
    t.index ["cpp_eve_item_id"], name: "index_components_on_cpp_eve_item_id"
  end

  create_table "blueprint_materials", id: :serial, force: :cascade do |t|
    t.integer "blueprint_id", null: false
    t.integer "blueprint_component_id", null: false
    t.integer "required_qtt", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["blueprint_component_id"], name: "index_blueprint_materials_on_blueprint_component_id"
    t.index ["blueprint_id"], name: "index_blueprint_materials_on_blueprint_id"
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
    t.bigint "blueprint_component_id", null: false
    t.bigint "station_detail_id"
    t.bigint "quantity", null: false
    t.boolean "touched", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["blueprint_component_id"], name: "index_bpc_assets_on_blueprint_component_id"
    t.index ["station_detail_id"], name: "index_bpc_assets_on_station_detail_id"
  end

  create_table "bpc_jita_sales_finals", force: :cascade do |t|
    t.bigint "blueprint_component_id"
    t.bigint "volume", null: false
    t.float "price", null: false
    t.bigint "cpp_order_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["blueprint_component_id"], name: "index_bpc_jita_sales_finals_on_blueprint_component_id"
  end

  create_table "bpc_prices_mins", force: :cascade do |t|
    t.bigint "trade_hub_id", null: false
    t.bigint "blueprint_component_id", null: false
    t.bigint "volume"
    t.float "price", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["blueprint_component_id"], name: "index_bpc_prices_mins_on_blueprint_component_id"
    t.index ["trade_hub_id"], name: "index_bpc_prices_mins_on_trade_hub_id"
  end

  create_table "characters", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "name", null: false
    t.integer "eve_id", null: false
    t.datetime "expires_on", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "token"
    t.string "renew_token"
    t.boolean "locked", default: false, null: false
    t.boolean "download_my_assets", default: false, null: false
    t.boolean "download_assets_running", default: false, null: false
    t.datetime "last_assets_download"
    t.bigint "character_pl_share_id"
    t.index ["character_pl_share_id"], name: "index_characters_on_character_pl_share_id"
    t.index ["download_my_assets"], name: "index_characters_on_download_my_assets"
    t.index ["user_id"], name: "index_characters_on_user_id"
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
    t.bigint "blueprint_id", null: false
    t.index "lower((name)::text)", name: "index_eve_items_on_lower_name", unique: true
    t.index ["blueprint_id"], name: "index_eve_items_on_blueprint_id"
    t.index ["cpp_eve_item_id"], name: "index_eve_items_on_cpp_eve_item_id"
    t.index ["market_group_id"], name: "index_eve_items_on_market_group_id"
  end

  create_table "eve_items_users", id: :serial, force: :cascade do |t|
    t.integer "user_id"
    t.integer "eve_item_id"
    t.index ["eve_item_id"], name: "index_eve_items_users_on_eve_item_id"
    t.index ["user_id"], name: "index_eve_items_users_on_user_id"
  end

  create_table "identities", id: :serial, force: :cascade do |t|
    t.string "name"
    t.string "email"
    t.string "password_digest"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "jita_margins", id: :serial, force: :cascade do |t|
    t.integer "eve_item_id"
    t.float "margin"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.float "margin_percent"
    t.float "jita_min_price"
    t.float "cost"
    t.bigint "mens_volume", default: 0, null: false
    t.bigint "batch_size", default: 0, null: false
    t.index ["eve_item_id"], name: "index_jita_margins_on_eve_item_id"
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
    t.integer "region_id"
    t.bigint "vol_month"
    t.bigint "vol_day"
    t.float "cost"
    t.float "min_price"
    t.float "avg_price"
    t.float "daily_monthly_pcent"
    t.integer "full_batch_size"
    t.integer "prod_qtt"
    t.float "single_unit_cost"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.float "margin_percent"
    t.index ["eve_item_id"], name: "index_prices_advices_on_eve_item_id"
    t.index ["margin_percent"], name: "index_prices_advices_on_margin_percent"
    t.index ["region_id"], name: "index_prices_advices_on_region_id"
    t.index ["trade_hub_id"], name: "index_prices_advices_on_trade_hub_id"
  end

  create_table "prices_avg_weeks", force: :cascade do |t|
    t.bigint "trade_hub_id", null: false
    t.bigint "eve_item_id", null: false
    t.float "price", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["trade_hub_id", "eve_item_id"], name: "index_prices_avg_weeks_on_trade_hub_id_and_eve_item_id", unique: true
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

  create_table "production_list_share_requests", force: :cascade do |t|
    t.bigint "sender_id", null: false
    t.bigint "recipient_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["recipient_id", "sender_id"], name: "plsr_unique_index", unique: true
  end

  create_table "production_lists", id: :serial, force: :cascade do |t|
    t.integer "user_id", null: false
    t.integer "trade_hub_id", null: false
    t.integer "eve_item_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "quantity_to_produce"
    t.integer "runs_count", limit: 2
    t.index ["eve_item_id"], name: "index_production_lists_on_eve_item_id"
    t.index ["trade_hub_id"], name: "index_production_lists_on_trade_hub_id"
    t.index ["user_id"], name: "index_production_lists_on_user_id"
  end

  create_table "regions", id: :serial, force: :cascade do |t|
    t.string "cpp_region_id", null: false
    t.string "name", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
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

  create_table "sales_orders", force: :cascade do |t|
    t.date "day", null: false
    t.bigint "volume", null: false
    t.float "price", null: false
    t.bigint "order_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "trade_hub_id", null: false
    t.bigint "eve_item_id", null: false
    t.integer "retrieve_session_id"
    t.boolean "closed", default: false
    t.time "issued"
    t.integer "duration"
    t.time "end_time"
    t.index ["eve_item_id"], name: "index_sales_orders_on_eve_item_id"
    t.index ["order_id", "volume"], name: "index_sales_orders_on_order_id_and_volume", unique: true
    t.index ["trade_hub_id"], name: "index_sales_orders_on_trade_hub_id"
  end

  create_table "sales_orders_process_infos", force: :cascade do |t|
    t.string "key", null: false
    t.integer "last_retrieve_session_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "station_details", force: :cascade do |t|
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
    t.hstore "industry_costs_indices"
    t.index ["cpp_station_id"], name: "index_station_details_on_cpp_station_id", unique: true
    t.index ["station_id"], name: "index_station_details_on_station_id"
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
    t.bigint "trade_hub_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.boolean "forbidden", default: true, null: false
    t.index ["forbidden"], name: "index_structures_on_forbidden"
    t.index ["trade_hub_id"], name: "index_structures_on_trade_hub_id"
  end

  create_table "trade_hubs", id: :serial, force: :cascade do |t|
    t.integer "eve_system_id", null: false
    t.string "name", null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer "region_id"
    t.boolean "inner", default: false, null: false
    t.index ["region_id"], name: "index_trade_hubs_on_region_id"
  end

  create_table "trade_hubs_users", id: :serial, force: :cascade do |t|
    t.integer "user_id"
    t.integer "trade_hub_id"
    t.index ["trade_hub_id"], name: "index_trade_hubs_users_on_trade_hub_id"
    t.index ["user_id"], name: "index_trade_hubs_users_on_user_id"
  end

  create_table "type_in_regions", force: :cascade do |t|
    t.integer "cpp_region_id", null: false
    t.integer "cpp_type_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["cpp_region_id"], name: "index_type_in_regions_on_cpp_region_id"
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
    t.datetime "created_at"
    t.datetime "updated_at"
    t.float "price"
    t.index ["eve_item_id"], name: "index_user_sale_orders_on_eve_item_id"
    t.index ["trade_hub_id"], name: "index_user_sale_orders_on_trade_hub_id"
    t.index ["user_id"], name: "index_user_sale_orders_on_user_id"
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
    t.bigint "user_pl_share_id"
    t.boolean "download_orders_running", default: false, null: false
    t.datetime "last_orders_download"
  end

  add_foreign_key "blueprint_component_sales_orders", "blueprint_components"
  add_foreign_key "blueprint_component_sales_orders", "trade_hubs"
  add_foreign_key "blueprint_materials", "blueprint_components"
  add_foreign_key "blueprint_materials", "blueprints"
  add_foreign_key "blueprint_modifications", "blueprints"
  add_foreign_key "blueprint_modifications", "users"
  add_foreign_key "bpc_assets", "blueprint_components"
  add_foreign_key "bpc_assets", "station_details"
  add_foreign_key "bpc_assets", "users"
  add_foreign_key "bpc_jita_sales_finals", "blueprint_components"
  add_foreign_key "bpc_prices_mins", "blueprint_components"
  add_foreign_key "bpc_prices_mins", "trade_hubs"
  add_foreign_key "characters", "characters", column: "character_pl_share_id"
  add_foreign_key "characters", "users"
  add_foreign_key "eve_items", "blueprints"
  add_foreign_key "eve_items", "market_groups"
  add_foreign_key "prices_advices", "eve_items"
  add_foreign_key "prices_advices", "regions"
  add_foreign_key "prices_advices", "trade_hubs"
  add_foreign_key "prices_avg_weeks", "eve_items"
  add_foreign_key "prices_avg_weeks", "trade_hubs"
  add_foreign_key "production_list_share_requests", "users", column: "recipient_id"
  add_foreign_key "production_list_share_requests", "users", column: "sender_id"
  add_foreign_key "production_lists", "eve_items"
  add_foreign_key "production_lists", "trade_hubs"
  add_foreign_key "production_lists", "users"
  add_foreign_key "sales_finals", "eve_items"
  add_foreign_key "sales_finals", "trade_hubs"
  add_foreign_key "sales_orders", "eve_items"
  add_foreign_key "sales_orders", "trade_hubs"
  add_foreign_key "station_details", "stations"
  add_foreign_key "structures", "trade_hubs"
  add_foreign_key "trade_hubs", "regions"
  add_foreign_key "users", "users", column: "user_pl_share_id"

  create_view "component_to_buys",  sql_definition: <<-SQL
      SELECT bc.id,
      eiu.user_id,
      bc.name,
      (sum((ceil(((bm.required_qtt)::double precision * bmo.percent_modification_value)) * (pl.runs_count)::double precision)) - (COALESCE(ba.quantity, (0)::bigint))::double precision) AS qtt_to_buy,
      ((sum((ceil(((bm.required_qtt)::double precision * bmo.percent_modification_value)) * (pl.runs_count)::double precision)) - (COALESCE(ba.quantity, (0)::bigint))::double precision) * bc.cost) AS total_cost
     FROM (((((((production_lists pl
       JOIN eve_items ei ON ((ei.id = pl.eve_item_id)))
       JOIN eve_items_users eiu ON ((ei.id = eiu.eve_item_id)))
       JOIN blueprints b ON ((ei.blueprint_id = b.id)))
       JOIN blueprint_materials bm ON ((b.id = bm.blueprint_id)))
       JOIN blueprint_components bc ON ((bm.blueprint_component_id = bc.id)))
       JOIN blueprint_modifications bmo ON (((b.id = bmo.blueprint_id) AND (bmo.user_id = eiu.user_id))))
       LEFT JOIN bpc_assets ba ON ((bc.id = ba.blueprint_component_id)))
    WHERE (pl.runs_count IS NOT NULL)
    GROUP BY bc.id, eiu.user_id, bc.name, COALESCE(ba.quantity, (0)::bigint)
   HAVING ((sum((ceil(((bm.required_qtt)::double precision * bmo.percent_modification_value)) * (pl.runs_count)::double precision)) - (COALESCE(ba.quantity, (0)::bigint))::double precision) > (0)::double precision);
  SQL

end

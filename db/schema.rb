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

ActiveRecord::Schema.define(version: 2018_06_23_140601) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "api_key_errors", id: :serial, force: :cascade do |t|
    t.integer "user_id"
    t.string "error_message"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "user_message"
    t.index ["user_id"], name: "index_api_key_errors_on_user_id"
  end

  create_table "blueprints", id: :serial, force: :cascade do |t|
    t.integer "eve_item_id"
    t.integer "nb_runs"
    t.integer "prod_qtt"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer "cpp_blueprint_id"
    t.index ["eve_item_id"], name: "index_blueprints_on_eve_item_id"
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
    t.index ["user_id"], name: "index_characters_on_user_id"
  end

  create_table "components", id: :serial, force: :cascade do |t|
    t.integer "cpp_eve_item_id"
    t.string "name", limit: 255
    t.float "cost"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer "blueprints_count"
    t.index ["cpp_eve_item_id"], name: "index_components_on_cpp_eve_item_id"
  end

  create_table "crest_prices_last_month_averages", id: :serial, force: :cascade do |t|
    t.integer "region_id", null: false
    t.integer "eve_item_id", null: false
    t.bigint "order_count_sum"
    t.bigint "volume_sum"
    t.bigint "order_count_avg"
    t.bigint "volume_avg"
    t.float "low_price_avg"
    t.float "avg_price_avg"
    t.float "high_price_avg"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["eve_item_id"], name: "index_crest_prices_last_month_averages_on_eve_item_id"
    t.index ["region_id"], name: "index_crest_prices_last_month_averages_on_region_id"
  end

  create_table "crontabs", force: :cascade do |t|
    t.string "cron_name", null: false
    t.boolean "status", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "eve_empty_market_histories", force: :cascade do |t|
    t.integer "cpp_region_id"
    t.integer "cpp_eve_item_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["cpp_region_id", "cpp_eve_item_id"], name: "idx_eve_empty_market_histories", unique: true
  end

  create_table "eve_items", id: :serial, force: :cascade do |t|
    t.integer "cpp_eve_item_id", null: false
    t.string "name", limit: 255, null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string "name_lowcase", limit: 255
    t.float "cost"
    t.boolean "epic_blueprint", default: false
    t.boolean "involved_in_blueprint", default: false
    t.integer "market_group_id"
    t.index ["cpp_eve_item_id"], name: "index_eve_items_on_cpp_eve_item_id"
    t.index ["market_group_id"], name: "index_eve_items_on_market_group_id"
  end

  create_table "eve_items_users", id: :serial, force: :cascade do |t|
    t.integer "user_id"
    t.integer "eve_item_id"
    t.index ["eve_item_id"], name: "index_eve_items_users_on_eve_item_id"
    t.index ["user_id"], name: "index_eve_items_users_on_user_id"
  end

  create_table "eve_market_history_errors", force: :cascade do |t|
    t.integer "cpp_region_id"
    t.integer "cpp_eve_item_id"
    t.string "error"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end

  create_table "eve_markets_histories", id: :serial, force: :cascade do |t|
    t.integer "region_id", null: false
    t.integer "eve_item_id", null: false
    t.string "day_timestamp"
    t.datetime "history_date", null: false
    t.bigint "order_count"
    t.bigint "volume"
    t.float "low_price"
    t.float "avg_price"
    t.float "high_price"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["day_timestamp"], name: "index_eve_markets_histories_on_day_timestamp"
    t.index ["history_date"], name: "index_eve_markets_histories_on_history_date"
    t.index ["region_id", "eve_item_id", "day_timestamp"], name: "price_histories_all_keys_index", unique: true
    t.index ["region_id", "eve_item_id"], name: "index_crest_price_histories_on_region_and_item"
  end

  create_table "eve_markets_prices", force: :cascade do |t|
    t.integer "type_id", null: false
    t.float "average_price"
    t.float "adjusted_price", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["type_id"], name: "index_eve_markets_prices_on_type_id", unique: true
  end

  create_table "identities", id: :serial, force: :cascade do |t|
    t.string "name", limit: 255
    t.string "email", limit: 255
    t.string "password_digest", limit: 255
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

  create_table "materials", id: :serial, force: :cascade do |t|
    t.integer "blueprint_id", null: false
    t.integer "component_id", null: false
    t.integer "required_qtt", null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.index ["blueprint_id"], name: "index_materials_on_blueprint_id"
    t.index ["component_id"], name: "index_materials_on_component_id"
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
    t.index ["eve_item_id"], name: "index_prices_advices_on_eve_item_id"
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

  create_table "shopping_baskets", id: :serial, force: :cascade do |t|
    t.integer "user_id", null: false
    t.integer "trade_hub_id", null: false
    t.integer "eve_item_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["eve_item_id"], name: "index_shopping_baskets_on_eve_item_id"
    t.index ["trade_hub_id"], name: "index_shopping_baskets_on_trade_hub_id"
    t.index ["user_id"], name: "index_shopping_baskets_on_user_id"
  end

  create_table "stations", id: :serial, force: :cascade do |t|
    t.integer "trade_hub_id"
    t.string "name", limit: 255
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
    t.string "name", limit: 255, null: false
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

  create_table "trade_orders", id: :serial, force: :cascade do |t|
    t.integer "user_id", null: false
    t.integer "eve_item_id", null: false
    t.integer "trade_hub_id", null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.float "price"
    t.index ["eve_item_id"], name: "index_trade_orders_on_eve_item_id"
    t.index ["trade_hub_id"], name: "index_trade_orders_on_trade_hub_id"
    t.index ["user_id"], name: "index_trade_orders_on_user_id"
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

  create_table "users", id: :serial, force: :cascade do |t|
    t.string "name", limit: 255
    t.boolean "remove_occuped_places"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string "provider", limit: 255
    t.string "uid", limit: 255
    t.datetime "last_changes_in_choices"
    t.integer "min_pcent_for_advice"
    t.boolean "watch_my_prices"
    t.float "min_amount_for_advice"
    t.boolean "admin", default: false, null: false
    t.boolean "batch_cap", default: true, null: false
    t.integer "vol_month_pcent", default: 10, null: false
    t.bigint "last_used_character_id"
    t.index ["last_used_character_id"], name: "index_users_on_last_used_character_id"
  end

  add_foreign_key "api_key_errors", "users"
  add_foreign_key "blueprints", "eve_items"
  add_foreign_key "characters", "users"
  add_foreign_key "crest_prices_last_month_averages", "eve_items"
  add_foreign_key "crest_prices_last_month_averages", "regions"
  add_foreign_key "eve_items", "market_groups"
  add_foreign_key "eve_markets_histories", "eve_items"
  add_foreign_key "eve_markets_histories", "regions"
  add_foreign_key "prices_advices", "eve_items"
  add_foreign_key "prices_advices", "regions"
  add_foreign_key "prices_advices", "trade_hubs"
  add_foreign_key "prices_avg_weeks", "eve_items"
  add_foreign_key "prices_avg_weeks", "trade_hubs"
  add_foreign_key "sales_finals", "eve_items"
  add_foreign_key "sales_finals", "trade_hubs"
  add_foreign_key "sales_orders", "eve_items"
  add_foreign_key "sales_orders", "trade_hubs"
  add_foreign_key "shopping_baskets", "eve_items"
  add_foreign_key "shopping_baskets", "trade_hubs"
  add_foreign_key "shopping_baskets", "users"
  add_foreign_key "structures", "trade_hubs"
  add_foreign_key "trade_hubs", "regions"
  add_foreign_key "users", "characters", column: "last_used_character_id"
end

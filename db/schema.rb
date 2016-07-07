# encoding: UTF-8
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

ActiveRecord::Schema.define(version: 20160703142622) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "api_key_errors", force: :cascade do |t|
    t.integer  "user_id"
    t.string   "error_message"
    t.datetime "created_at",    null: false
    t.datetime "updated_at",    null: false
    t.string   "user_message"
  end

  add_index "api_key_errors", ["user_id"], name: "index_api_key_errors_on_user_id", using: :btree

  create_table "blueprints", force: :cascade do |t|
    t.integer  "eve_item_id"
    t.integer  "nb_runs"
    t.integer  "prod_qtt"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "cpp_blueprint_id"
  end

  add_index "blueprints", ["cpp_blueprint_id"], name: "index_blueprints_on_cpp_blueprint_id", using: :btree
  add_index "blueprints", ["eve_item_id"], name: "index_blueprints_on_eve_item_id", using: :btree

  create_table "caddie_crest_price_history_updates", force: :cascade do |t|
    t.integer  "eve_item_id"
    t.integer  "region_id"
    t.date     "max_update"
    t.date     "max_eve_item_create"
    t.date     "max_region_create"
    t.date     "max_date"
    t.integer  "nb_days"
    t.string   "process_queue"
    t.integer  "process_queue_priority"
    t.date     "next_process_date"
    t.datetime "created_at",             null: false
    t.datetime "updated_at",             null: false
    t.integer  "thread_slice_id"
  end

  add_index "caddie_crest_price_history_updates", ["eve_item_id", "region_id"], name: "index_caddie_cphu_on_eve_item_id_and_region_id", unique: true, using: :btree

  create_table "components", force: :cascade do |t|
    t.integer  "cpp_eve_item_id"
    t.string   "name",            limit: 255
    t.float    "cost"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "components", ["cpp_eve_item_id"], name: "index_components_on_cpp_eve_item_id", using: :btree

  create_table "crest_costs", force: :cascade do |t|
    t.integer  "cpp_item_id",    null: false
    t.integer  "eve_item_id",    null: false
    t.float    "adjusted_price"
    t.float    "average_price"
    t.float    "cost"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "crest_costs", ["cpp_item_id"], name: "index_crest_costs_on_cpp_item_id", unique: true, using: :btree
  add_index "crest_costs", ["eve_item_id"], name: "index_crest_costs_on_eve_item_id", unique: true, using: :btree

  create_table "crest_price_histories", force: :cascade do |t|
    t.integer  "region_id",               null: false
    t.integer  "eve_item_id",             null: false
    t.string   "day_timestamp",           null: false
    t.datetime "history_date",            null: false
    t.integer  "order_count",   limit: 8
    t.integer  "volume",        limit: 8
    t.float    "low_price"
    t.float    "avg_price"
    t.float    "high_price"
    t.datetime "created_at",              null: false
    t.datetime "updated_at",              null: false
  end

  add_index "crest_price_histories", ["day_timestamp"], name: "index_crest_price_histories_on_day_timestamp", using: :btree
  add_index "crest_price_histories", ["eve_item_id"], name: "index_crest_price_histories_on_eve_item_id", using: :btree
  add_index "crest_price_histories", ["history_date"], name: "index_crest_price_histories_on_history_date", using: :btree
  add_index "crest_price_histories", ["region_id", "eve_item_id", "day_timestamp"], name: "price_histories_all_keys_index", unique: true, using: :btree
  add_index "crest_price_histories", ["region_id"], name: "index_crest_price_histories_on_region_id", using: :btree

  create_table "crest_price_histories_daily_used", id: false, force: :cascade do |t|
    t.integer  "eve_item_id"
    t.integer  "region_id"
    t.datetime "max"
    t.datetime "items_created_at"
    t.datetime "regions_created_at"
  end

  create_table "crest_price_histories_frequently_used", id: false, force: :cascade do |t|
    t.integer  "eve_item_id"
    t.integer  "region_id"
    t.datetime "updated_at"
    t.datetime "items_created_at"
    t.datetime "regions_created_at"
  end

  create_table "crest_price_histories_never_used", id: false, force: :cascade do |t|
    t.integer "eve_items_id"
    t.integer "regions_id"
  end

  create_table "crest_price_histories_rarely_used", id: false, force: :cascade do |t|
    t.integer "eve_items_id"
    t.integer "regions_id"
  end

  create_table "crest_prices_last_month_averages", force: :cascade do |t|
    t.integer  "region_id",                 null: false
    t.integer  "eve_item_id",               null: false
    t.integer  "order_count_sum", limit: 8
    t.integer  "volume_sum",      limit: 8
    t.integer  "order_count_avg", limit: 8
    t.integer  "volume_avg",      limit: 8
    t.float    "low_price_avg"
    t.float    "avg_price_avg"
    t.float    "high_price_avg"
    t.datetime "created_at",                null: false
    t.datetime "updated_at",                null: false
  end

  add_index "crest_prices_last_month_averages", ["eve_item_id"], name: "index_crest_prices_last_month_averages_on_eve_item_id", using: :btree
  add_index "crest_prices_last_month_averages", ["region_id", "eve_item_id"], name: "prices_lmavg_all_keys_index", unique: true, using: :btree
  add_index "crest_prices_last_month_averages", ["region_id"], name: "index_crest_prices_last_month_averages_on_region_id", using: :btree

  create_table "eve_clients", force: :cascade do |t|
    t.string   "cpp_client_id", limit: 255, null: false
    t.string   "name",          limit: 255, null: false
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "eve_clients", ["cpp_client_id"], name: "index_eve_clients_on_cpp_client_id", unique: true, using: :btree

  create_table "eve_items", force: :cascade do |t|
    t.integer  "cpp_eve_item_id"
    t.string   "name",                  limit: 255,                 null: false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "name_lowcase",          limit: 255
    t.float    "cost"
    t.boolean  "epic_blueprint",                    default: false
    t.boolean  "involved_in_blueprint",             default: false
    t.integer  "market_group_id"
  end

  add_index "eve_items", ["cpp_eve_item_id"], name: "index_eve_items_on_cpp_eve_item_id", using: :btree
  add_index "eve_items", ["market_group_id"], name: "index_eve_items_on_market_group_id", using: :btree

  create_table "eve_items_users", force: :cascade do |t|
    t.integer "user_id"
    t.integer "eve_item_id"
  end

  add_index "eve_items_users", ["eve_item_id"], name: "index_eve_items_users_on_eve_item_id", using: :btree
  add_index "eve_items_users", ["user_id"], name: "index_eve_items_users_on_user_id", using: :btree

  create_table "identities", force: :cascade do |t|
    t.string   "name",            limit: 255
    t.string   "email",           limit: 255
    t.string   "password_digest", limit: 255
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "jita_margins", force: :cascade do |t|
    t.integer  "eve_item_id"
    t.float    "margin"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.float    "margin_percent"
    t.float    "jita_min_price"
    t.float    "cost"
    t.integer  "mens_volume",    limit: 8, default: 0, null: false
    t.integer  "batch_size",     limit: 8, default: 0, null: false
  end

  add_index "jita_margins", ["eve_item_id"], name: "index_jita_margins_on_eve_item_id", using: :btree

  create_table "market_group_hierarchies", id: false, force: :cascade do |t|
    t.integer "ancestor_id",   null: false
    t.integer "descendant_id", null: false
    t.integer "generations",   null: false
  end

  add_index "market_group_hierarchies", ["ancestor_id", "descendant_id", "generations"], name: "market_group_anc_desc_idx", unique: true, using: :btree
  add_index "market_group_hierarchies", ["descendant_id"], name: "market_group_desc_idx", using: :btree

  create_table "market_groups", force: :cascade do |t|
    t.string   "cpp_market_group_id", null: false
    t.string   "name",                null: false
    t.integer  "parent_id"
    t.datetime "created_at",          null: false
    t.datetime "updated_at",          null: false
  end

  add_index "market_groups", ["cpp_market_group_id"], name: "index_market_groups_on_cpp_market_group_id", unique: true, using: :btree

  create_table "materials", force: :cascade do |t|
    t.integer  "blueprint_id"
    t.integer  "component_id"
    t.integer  "required_qtt"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "materials", ["blueprint_id"], name: "index_materials_on_blueprint_id", using: :btree
  add_index "materials", ["component_id"], name: "index_materials_on_component_id", using: :btree

  create_table "min_prices", force: :cascade do |t|
    t.integer  "eve_item_id"
    t.integer  "trade_hub_id"
    t.float    "min_price"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "min_prices", ["eve_item_id"], name: "index_min_prices_on_eve_item_id", using: :btree
  add_index "min_prices", ["trade_hub_id"], name: "index_min_prices_on_trade_hub_id", using: :btree

  create_table "min_prices_logs", force: :cascade do |t|
    t.string   "random_hash"
    t.datetime "retrieve_start"
    t.datetime "retrieve_end"
    t.integer  "duration"
    t.integer  "updated_items_count"
    t.datetime "created_at",          null: false
    t.datetime "updated_at",          null: false
  end

  create_table "regions", force: :cascade do |t|
    t.string   "cpp_region_id", null: false
    t.string   "name",          null: false
    t.datetime "created_at",    null: false
    t.datetime "updated_at",    null: false
  end

  add_index "regions", ["cpp_region_id"], name: "index_regions_on_cpp_region_id", unique: true, using: :btree

  create_table "sale_records", force: :cascade do |t|
    t.integer  "user_id",                           null: false
    t.integer  "eve_client_id",                     null: false
    t.integer  "eve_item_id",                       null: false
    t.integer  "station_id",                        null: false
    t.string   "eve_transaction_key",   limit: 255, null: false
    t.integer  "quantity",                          null: false
    t.float    "unit_sale_price",                   null: false
    t.float    "total_sale_price",                  null: false
    t.float    "unit_cost"
    t.float    "unit_sale_profit"
    t.float    "total_sale_profit"
    t.datetime "transaction_date_time",             null: false
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "sale_records", ["eve_client_id"], name: "index_sale_records_on_eve_client_id", using: :btree
  add_index "sale_records", ["eve_item_id"], name: "index_sale_records_on_eve_item_id", using: :btree
  add_index "sale_records", ["eve_transaction_key"], name: "index_sale_records_on_eve_transaction_key", unique: true, using: :btree
  add_index "sale_records", ["station_id"], name: "index_sale_records_on_station_id", using: :btree
  add_index "sale_records", ["user_id"], name: "index_sale_records_on_user_id", using: :btree

  create_table "shopping_baskets", force: :cascade do |t|
    t.integer  "user_id",      null: false
    t.integer  "trade_hub_id", null: false
    t.integer  "eve_item_id",  null: false
    t.datetime "created_at",   null: false
    t.datetime "updated_at",   null: false
  end

  add_index "shopping_baskets", ["eve_item_id"], name: "index_shopping_baskets_on_eve_item_id", using: :btree
  add_index "shopping_baskets", ["trade_hub_id"], name: "index_shopping_baskets_on_trade_hub_id", using: :btree
  add_index "shopping_baskets", ["user_id"], name: "index_shopping_baskets_on_user_id", using: :btree

  create_table "stations", force: :cascade do |t|
    t.integer  "trade_hub_id"
    t.string   "name",           limit: 255
    t.integer  "cpp_station_id"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "stations", ["cpp_station_id"], name: "index_stations_on_cpp_station_id", using: :btree
  add_index "stations", ["trade_hub_id"], name: "index_stations_on_trade_hub_id", using: :btree

  create_table "trade_hubs", force: :cascade do |t|
    t.integer  "eve_system_id"
    t.string   "name",          limit: 255
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "region_id"
    t.boolean  "inner",                     default: false
  end

  add_index "trade_hubs", ["region_id"], name: "index_trade_hubs_on_region_id", using: :btree

  create_table "trade_hubs_users", force: :cascade do |t|
    t.integer "user_id"
    t.integer "trade_hub_id"
  end

  add_index "trade_hubs_users", ["trade_hub_id"], name: "index_trade_hubs_users_on_trade_hub_id", using: :btree
  add_index "trade_hubs_users", ["user_id"], name: "index_trade_hubs_users_on_user_id", using: :btree

  create_table "trade_orders", force: :cascade do |t|
    t.integer  "user_id"
    t.integer  "eve_item_id"
    t.integer  "trade_hub_id"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.boolean  "new_order"
    t.float    "price"
  end

  add_index "trade_orders", ["eve_item_id"], name: "index_trade_orders_on_eve_item_id", using: :btree
  add_index "trade_orders", ["trade_hub_id"], name: "index_trade_orders_on_trade_hub_id", using: :btree
  add_index "trade_orders", ["user_id"], name: "index_trade_orders_on_user_id", using: :btree

  create_table "user_activity_logs", force: :cascade do |t|
    t.string   "ip"
    t.string   "action"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string   "user"
  end

  create_table "users", force: :cascade do |t|
    t.string   "name",                    limit: 255
    t.boolean  "remove_occuped_places"
    t.string   "key_user_id",             limit: 255
    t.string   "api_key",                 limit: 255
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "provider",                limit: 255
    t.string   "uid",                     limit: 255
    t.string   "oauth_token",             limit: 255
    t.datetime "oauth_expires_at"
    t.datetime "last_changes_in_choices"
    t.integer  "min_pcent_for_advice"
    t.boolean  "watch_my_prices"
    t.float    "min_amount_for_advice"
    t.boolean  "admin",                               default: false, null: false
  end

  add_foreign_key "api_key_errors", "users"
  add_foreign_key "blueprints", "eve_items"
  add_foreign_key "caddie_crest_price_history_updates", "eve_items"
  add_foreign_key "caddie_crest_price_history_updates", "regions"
  add_foreign_key "crest_costs", "eve_items"
  add_foreign_key "crest_price_histories", "eve_items"
  add_foreign_key "crest_price_histories", "regions"
  add_foreign_key "crest_prices_last_month_averages", "eve_items"
  add_foreign_key "crest_prices_last_month_averages", "regions"
  add_foreign_key "eve_items", "market_groups"
  add_foreign_key "shopping_baskets", "eve_items"
  add_foreign_key "shopping_baskets", "trade_hubs"
  add_foreign_key "shopping_baskets", "users"
  add_foreign_key "trade_hubs", "regions"
end

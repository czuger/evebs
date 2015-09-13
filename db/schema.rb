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

ActiveRecord::Schema.define(version: 20150913092820) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

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

  create_table "components", force: :cascade do |t|
    t.integer  "cpp_eve_item_id"
    t.string   "name"
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
  add_index "crest_price_histories", ["region_id", "eve_item_id", "day_timestamp"], name: "price_histories_all_keys_index", unique: true, using: :btree
  add_index "crest_price_histories", ["region_id"], name: "index_crest_price_histories_on_region_id", using: :btree

  create_table "crest_prices_last_month_averages", id: false, force: :cascade do |t|
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
    t.string   "cpp_client_id", null: false
    t.string   "name",          null: false
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "eve_clients", ["cpp_client_id"], name: "index_eve_clients_on_cpp_client_id", unique: true, using: :btree

  create_table "eve_items", force: :cascade do |t|
    t.integer  "cpp_eve_item_id"
    t.string   "name"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "name_lowcase"
    t.float    "cost"
    t.boolean  "epic_blueprint",        default: false
    t.integer  "cpp_market_group_id"
    t.boolean  "involved_in_blueprint", default: false
  end

  add_index "eve_items", ["cpp_eve_item_id"], name: "index_eve_items_on_cpp_eve_item_id", using: :btree
  add_index "eve_items", ["cpp_market_group_id"], name: "index_eve_items_on_cpp_market_group_id", using: :btree

  create_table "eve_items_users", force: :cascade do |t|
    t.integer "user_id"
    t.integer "eve_item_id"
  end

  add_index "eve_items_users", ["eve_item_id"], name: "index_eve_items_users_on_eve_item_id", using: :btree
  add_index "eve_items_users", ["user_id"], name: "index_eve_items_users_on_user_id", using: :btree

  create_table "identities", force: :cascade do |t|
    t.string   "name"
    t.string   "email"
    t.string   "password_digest"
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
  end

  add_index "jita_margins", ["eve_item_id"], name: "index_jita_margins_on_eve_item_id", using: :btree

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

  create_table "regions", force: :cascade do |t|
    t.string   "cpp_region_id", null: false
    t.string   "name",          null: false
    t.datetime "created_at",    null: false
    t.datetime "updated_at",    null: false
  end

  add_index "regions", ["cpp_region_id"], name: "index_regions_on_cpp_region_id", unique: true, using: :btree

  create_table "sale_records", force: :cascade do |t|
    t.integer  "user_id",               null: false
    t.integer  "eve_client_id",         null: false
    t.integer  "eve_item_id",           null: false
    t.integer  "station_id",            null: false
    t.string   "eve_transaction_key",   null: false
    t.integer  "quantity",              null: false
    t.float    "unit_sale_price",       null: false
    t.float    "total_sale_price",      null: false
    t.float    "unit_cost"
    t.float    "unit_sale_profit"
    t.float    "total_sale_profit"
    t.datetime "transaction_date_time", null: false
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "sale_records", ["eve_client_id"], name: "index_sale_records_on_eve_client_id", using: :btree
  add_index "sale_records", ["eve_item_id"], name: "index_sale_records_on_eve_item_id", using: :btree
  add_index "sale_records", ["eve_transaction_key"], name: "index_sale_records_on_eve_transaction_key", unique: true, using: :btree
  add_index "sale_records", ["station_id"], name: "index_sale_records_on_station_id", using: :btree
  add_index "sale_records", ["user_id"], name: "index_sale_records_on_user_id", using: :btree

  create_table "stations", force: :cascade do |t|
    t.integer  "trade_hub_id"
    t.string   "name"
    t.integer  "cpp_station_id"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "stations", ["cpp_station_id"], name: "index_stations_on_cpp_station_id", using: :btree
  add_index "stations", ["trade_hub_id"], name: "index_stations_on_trade_hub_id", using: :btree

  create_table "trade_hubs", force: :cascade do |t|
    t.integer  "eve_system_id"
    t.string   "name"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "region_id"
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

  create_table "users", force: :cascade do |t|
    t.string   "name"
    t.boolean  "remove_occuped_places"
    t.string   "key_user_id"
    t.string   "api_key"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "provider"
    t.string   "uid"
    t.string   "oauth_token"
    t.datetime "oauth_expires_at"
    t.datetime "last_changes_in_choices"
    t.integer  "min_pcent_for_advice"
    t.boolean  "watch_my_prices"
    t.float    "min_amount_for_advice"
  end

  add_foreign_key "crest_costs", "eve_items"
  add_foreign_key "crest_price_histories", "eve_items"
  add_foreign_key "crest_price_histories", "regions"
  add_foreign_key "crest_prices_last_month_averages", "eve_items"
  add_foreign_key "crest_prices_last_month_averages", "regions"
  add_foreign_key "trade_hubs", "regions"
end

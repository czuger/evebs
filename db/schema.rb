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

ActiveRecord::Schema.define(version: 20150811133912) do

  create_table "blueprints", force: true do |t|
    t.integer  "eve_item_id"
    t.integer  "nb_runs"
    t.integer  "prod_qtt"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "cpp_blueprint_id"
  end

  add_index "blueprints", ["cpp_blueprint_id"], name: "index_blueprints_on_cpp_blueprint_id"
  add_index "blueprints", ["eve_item_id"], name: "index_blueprints_on_eve_item_id"

  create_table "components", force: true do |t|
    t.integer  "cpp_eve_item_id"
    t.string   "name"
    t.float    "cost"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "components", ["cpp_eve_item_id"], name: "index_components_on_cpp_eve_item_id"

  create_table "eve_clients", force: true do |t|
    t.string   "cpp_client_id", null: false
    t.string   "name",          null: false
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "eve_clients", ["cpp_client_id"], name: "index_eve_clients_on_cpp_client_id", unique: true

  create_table "eve_items", force: true do |t|
    t.integer  "cpp_eve_item_id"
    t.string   "name"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "name_lowcase"
    t.float    "cost"
  end

  add_index "eve_items", ["cpp_eve_item_id"], name: "index_eve_items_on_cpp_eve_item_id"

  create_table "eve_items_users", force: true do |t|
    t.integer "user_id"
    t.integer "eve_item_id"
  end

  add_index "eve_items_users", ["eve_item_id"], name: "index_eve_items_users_on_eve_item_id"
  add_index "eve_items_users", ["user_id"], name: "index_eve_items_users_on_user_id"

  create_table "identities", force: true do |t|
    t.string   "name"
    t.string   "email"
    t.string   "password_digest"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "materials", force: true do |t|
    t.integer  "blueprint_id"
    t.integer  "component_id"
    t.integer  "required_qtt"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "materials", ["blueprint_id"], name: "index_materials_on_blueprint_id"
  add_index "materials", ["component_id"], name: "index_materials_on_component_id"

  create_table "min_prices", force: true do |t|
    t.integer  "eve_item_id"
    t.integer  "trade_hub_id"
    t.float    "min_price"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "min_prices", ["eve_item_id"], name: "index_min_prices_on_eve_item_id"
  add_index "min_prices", ["trade_hub_id"], name: "index_min_prices_on_trade_hub_id"

  create_table "sale_records", force: true do |t|
    t.integer  "user_id",             null: false
    t.integer  "eve_client_id",       null: false
    t.integer  "eve_item_id",         null: false
    t.integer  "station_id",          null: false
    t.string   "eve_transaction_key", null: false
    t.integer  "quantity",            null: false
    t.float    "unit_sale_price",     null: false
    t.float    "total_sale_price",    null: false
    t.float    "unit_cost"
    t.float    "unit_sale_profit"
    t.float    "total_sale_profit"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "sale_records", ["eve_client_id"], name: "index_sale_records_on_eve_client_id"
  add_index "sale_records", ["eve_item_id"], name: "index_sale_records_on_eve_item_id"
  add_index "sale_records", ["eve_transaction_key"], name: "index_sale_records_on_eve_transaction_key", unique: true
  add_index "sale_records", ["station_id"], name: "index_sale_records_on_station_id"
  add_index "sale_records", ["user_id"], name: "index_sale_records_on_user_id"

  create_table "stations", force: true do |t|
    t.integer  "trade_hub_id"
    t.string   "name"
    t.integer  "cpp_station_id"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "stations", ["cpp_station_id"], name: "index_stations_on_cpp_station_id"
  add_index "stations", ["trade_hub_id"], name: "index_stations_on_trade_hub_id"

  create_table "trade_hubs", force: true do |t|
    t.integer  "eve_system_id"
    t.string   "name"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "trade_hubs_users", force: true do |t|
    t.integer "user_id"
    t.integer "trade_hub_id"
  end

  add_index "trade_hubs_users", ["trade_hub_id"], name: "index_trade_hubs_users_on_trade_hub_id"
  add_index "trade_hubs_users", ["user_id"], name: "index_trade_hubs_users_on_user_id"

  create_table "trade_orders", force: true do |t|
    t.integer  "user_id"
    t.integer  "eve_item_id"
    t.integer  "trade_hub_id"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.boolean  "new_order"
    t.float    "price"
  end

  add_index "trade_orders", ["eve_item_id"], name: "index_trade_orders_on_eve_item_id"
  add_index "trade_orders", ["trade_hub_id"], name: "index_trade_orders_on_trade_hub_id"
  add_index "trade_orders", ["user_id"], name: "index_trade_orders_on_user_id"

  create_table "users", force: true do |t|
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

end

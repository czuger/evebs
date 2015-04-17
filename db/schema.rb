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

ActiveRecord::Schema.define(version: 20150417135716) do

  create_table "eve_items", force: true do |t|
    t.integer  "cpp_eve_item_id"
    t.string   "name"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "first_letter"
    t.string   "name_lowcase"
    t.float    "cost"
  end

  add_index "eve_items", ["cpp_eve_item_id"], name: "index_eve_items_on_cpp_eve_item_id"
  add_index "eve_items", ["first_letter"], name: "index_eve_items_on_first_letter"

  create_table "eve_items_users", force: true do |t|
    t.integer "user_id"
    t.integer "eve_item_id"
  end

  add_index "eve_items_users", ["eve_item_id"], name: "index_eve_items_users_on_eve_item_id"
  add_index "eve_items_users", ["user_id"], name: "index_eve_items_users_on_user_id"

  create_table "min_prices", force: true do |t|
    t.integer  "eve_item_id"
    t.integer  "trade_hub_id"
    t.float    "min_price"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "min_prices", ["eve_item_id"], name: "index_min_prices_on_eve_item_id"
  add_index "min_prices", ["trade_hub_id"], name: "index_min_prices_on_trade_hub_id"

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

  create_table "users", force: true do |t|
    t.string   "name"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

end

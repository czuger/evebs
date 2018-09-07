# require 'open-uri'
# # require 'open-uri/cached'
require 'pp'

class EveItem < ApplicationRecord

  include Assert

  has_and_belongs_to_many :users
  belongs_to :blueprint

  has_many :blueprint_materials, dependent: :destroy
  has_many :blueprint_components, through: :materials
  belongs_to :market_group

  has_many :prices_mins, dependent: :delete_all
  has_many :sales_finals, dependent: :delete_all
  has_many :prices_advices, dependent: :delete_all
  has_many :sales_orders, dependent: :delete_all
  has_many :buy_orders, dependent: :delete_all
  has_many :buy_orders_analytics, dependent: :delete_all

  def self.to_eve_item_id(cpp_eve_item_id)
    eve_item=EveItem.where( 'cpp_eve_item_id=?', cpp_eve_item_id).first
    eve_item ? eve_item.id : nil
  end

  def self.used_items
    used_items, dummy = User.get_used_items_and_trade_hubs
    used_items
  end

end

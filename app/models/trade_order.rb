require_relative 'trade_orders/get_full_order_list'

require 'pp'

class TradeOrder < ApplicationRecord
  belongs_to :user
  belongs_to :eve_item
  belongs_to :trade_hub
end

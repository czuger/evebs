class User < ActiveRecord::Base
  has_and_belongs_to_many :eve_items
  has_and_belongs_to_many :trade_hubs
end

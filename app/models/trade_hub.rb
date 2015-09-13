class TradeHub < ActiveRecord::Base
  has_many :min_prices
  belongs_to :region
end

class Region < ApplicationRecord
  has_many :trade_hubs
  has_many :crest_prices_last_month_averages
end

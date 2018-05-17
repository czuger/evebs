class Region < ApplicationRecord
  has_many :trade_hubs
  has_many :crest_prices_last_month_averages

  has_many :type_in_regions, foreign_key: :cpp_region_id, primary_key: :cpp_region_id

  has_many :eve_items_in_market, through: :type_in_regions, class_name: 'EveItem', source: :eve_items

end

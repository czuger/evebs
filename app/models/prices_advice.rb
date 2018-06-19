class PricesAdvice < ApplicationRecord

  belongs_to :eve_item
  belongs_to :trade_hub
  belongs_to :region

end
class BuyOrdersAnalyticsResult < ApplicationRecord
  belongs_to :trade_hub
  belongs_to :eve_item
end

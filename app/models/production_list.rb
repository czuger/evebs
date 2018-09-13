class ProductionList < ApplicationRecord
  belongs_to :trade_hub
  belongs_to :eve_item
  belongs_to :user
end

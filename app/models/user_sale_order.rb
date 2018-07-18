class UserSaleOrder < ApplicationRecord
  belongs_to :user
  belongs_to :eve_item
  belongs_to :trade_hub
end

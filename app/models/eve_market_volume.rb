class EveMarketVolume < ApplicationRecord
  belongs_to :region
  belongs_to :eve_item
end
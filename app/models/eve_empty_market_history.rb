class EveEmptyMarketHistory < ApplicationRecord
  belongs_to :eve_item
  belongs_to :region
end

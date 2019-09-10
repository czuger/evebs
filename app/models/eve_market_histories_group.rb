class EveMarketHistoriesGroup < ApplicationRecord
  belongs_to :universe_region
  belongs_to :eve_item
end

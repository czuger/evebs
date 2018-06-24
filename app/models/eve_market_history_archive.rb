class EveMarketHistoryArchive < ApplicationRecord
  belongs_to :eve_item
  belongs_to :region
end

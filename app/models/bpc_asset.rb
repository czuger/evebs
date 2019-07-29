class BpcAsset < ApplicationRecord

  CACHE_DURATION = 3600

  belongs_to :universe_station
  belongs_to :eve_item
  belongs_to :user
end

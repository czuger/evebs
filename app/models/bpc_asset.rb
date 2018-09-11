class BpcAsset < ApplicationRecord

  CACHE_DURATION = 3600

  belongs_to :station_detail
  belongs_to :eve_item
end

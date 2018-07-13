class BpcAsset < ApplicationRecord
  belongs_to :station_detail
  belongs_to :blueprint_component
end

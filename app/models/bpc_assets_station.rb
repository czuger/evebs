class BpcAssetsStation < ApplicationRecord
  belongs_to :user
  belongs_to :station_detail
end

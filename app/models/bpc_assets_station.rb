class BpcAssetsStation < ApplicationRecord
  belongs_to :user
  belongs_to :universe_station
end

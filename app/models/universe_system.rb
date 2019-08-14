class UniverseSystem < ApplicationRecord
  has_many :universe_stations
  belongs_to :universe_constellation
  delegate :region, :to => :universe_constellation
end

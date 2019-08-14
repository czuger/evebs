class UniverseRegion < ApplicationRecord
  has_many :universe_constellations
  has_many :universe_systems, through: :universe_constellations
end

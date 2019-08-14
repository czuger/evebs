class UniverseConstellation < ApplicationRecord
  has_many :universe_systems
  belongs_to :universe_region
end

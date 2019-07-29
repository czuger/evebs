class UniverseStation < ApplicationRecord
  belongs_to :station
  belongs_to :universe_system
end

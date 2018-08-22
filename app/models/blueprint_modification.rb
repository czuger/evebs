class BlueprintModification < ApplicationRecord

  CACHE_DURATION = 3600

  belongs_to :user
  belongs_to :blueprint
end

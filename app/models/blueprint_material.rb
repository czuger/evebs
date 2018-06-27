class BlueprintMaterial < ApplicationRecord
  belongs_to :blueprint
  belongs_to :blueprint_component, dependent: :destroy
end

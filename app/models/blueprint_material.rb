class BlueprintMaterial < ApplicationRecord
  belongs_to :blueprint
  belongs_to :eve_item
end

class BlueprintComponentSalesOrder < ApplicationRecord
  belongs_to :trade_hub
  belongs_to :blueprint_component
end

class ProductionListShareRequest < ApplicationRecord
  belongs_to :sender, class_name: 'Character'
end

class Material < ApplicationRecord
  belongs_to :blueprint
  belongs_to :component
  validates :blueprint_id, :component_id, :required_qtt, presence: true
end

class Material < ApplicationRecord
  belongs_to :blueprint
  belongs_to :component, dependent: :destroy
end

class EveItemsSavedList < ApplicationRecord
  belongs_to :user

  serialize :saved_ids
end

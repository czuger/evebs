class MarketGroup < ApplicationRecord

  has_many :eve_items, dependent: :destroy
  serialize :cpp_type_ids
  acts_as_tree

end

class TypeInRegion < ApplicationRecord
  has_many :eve_items, primary_key: :cpp_type_id, foreign_key: :cpp_eve_item_id
end

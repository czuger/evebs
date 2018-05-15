class SetCppEveItemIdNotNullInEveItem < ActiveRecord::Migration[5.2]
  def change
    change_column :eve_items, :cpp_eve_item_id, :integer, null: false
  end
end

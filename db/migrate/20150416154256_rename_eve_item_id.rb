class RenameEveItemId < ActiveRecord::Migration[4.2]
  def change
    rename_column :eve_items, :eve_item_id, :cpp_eve_item_id
  end
end

class RenameEveItemId < ActiveRecord::Migration
  def change
    rename_column :eve_items, :eve_item_id, :cpp_eve_item_id
  end
end

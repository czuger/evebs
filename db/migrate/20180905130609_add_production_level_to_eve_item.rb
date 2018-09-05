class AddProductionLevelToEveItem < ActiveRecord::Migration[5.2]
  def change
    add_column :eve_items, :production_level, :integer, null: false, default: 0
    add_column :eve_items, :base_item, :boolean, null: false, default: false
  end
end

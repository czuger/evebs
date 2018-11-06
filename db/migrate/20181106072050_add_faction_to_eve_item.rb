class AddFactionToEveItem < ActiveRecord::Migration[5.2]
  def change
    add_column :eve_items, :faction, :boolean, null: false, default: false
  end
end

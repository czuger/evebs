class AddEpicBlueprintToEveItem < ActiveRecord::Migration[4.2]
  def change
    add_column :eve_items, :epic_blueprint, :boolean, default: false
  end
end

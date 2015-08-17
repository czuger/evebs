class AddEpicBlueprintToEveItem < ActiveRecord::Migration
  def change
    add_column :eve_items, :epic_blueprint, :boolean, default: false
  end
end

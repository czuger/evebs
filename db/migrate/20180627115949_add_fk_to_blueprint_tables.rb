class AddFkToBlueprintTables < ActiveRecord::Migration[5.2]
  def change
    rename_column :blueprint_materials, :component_id, :blueprint_component_id
    add_foreign_key :blueprint_materials, :blueprints
    add_foreign_key :blueprint_materials, :blueprint_components
    remove_column :blueprint_components, :blueprints_count
  end
end

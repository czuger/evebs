class RenameMaterialToBlueprintMaterial < ActiveRecord::Migration[5.2]
  def change
    rename_table :materials, :blueprint_materials
  end
end

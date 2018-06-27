class RenameComponentToBlueprintComponent < ActiveRecord::Migration[5.2]
  def change
    rename_table :components, :blueprint_components
  end
end

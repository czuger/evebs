class AddVolumeToBlueprintComponent < ActiveRecord::Migration[5.2]
  def change
    add_column :blueprint_components, :volume, :float
  end
end

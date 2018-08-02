class VolumeNotNullInBpc < ActiveRecord::Migration[5.2]
  def change
    change_column :blueprint_components, :volume, :float, null: false
  end
end

class ChangeVolumeOnEveItemToFloat < ActiveRecord::Migration[5.2]
  def change
    drop_view :component_to_buys
    change_column :eve_items, :volume, :float
  end
end

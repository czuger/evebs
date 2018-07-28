class BlueprintComponentCppEveItemIdIndexUnique < ActiveRecord::Migration[5.2]
  def change
    remove_index :blueprint_components, :cpp_eve_item_id
    add_index :blueprint_components, :cpp_eve_item_id, unique: :true
  end
end

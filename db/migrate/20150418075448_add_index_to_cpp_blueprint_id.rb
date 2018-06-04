class AddIndexToCppBlueprintId < ActiveRecord::Migration[4.2]
  def change
    add_index :blueprints, :cpp_blueprint_id
  end
end

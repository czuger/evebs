class AddIndexToCppBlueprintId < ActiveRecord::Migration
  def change
    add_index :blueprints, :cpp_blueprint_id
  end
end

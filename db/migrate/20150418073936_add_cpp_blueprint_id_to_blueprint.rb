class AddCppBlueprintIdToBlueprint < ActiveRecord::Migration
  def change
    add_column :blueprints, :cpp_blueprint_id, :integer
  end
end

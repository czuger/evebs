class AddCppBlueprintIdToBlueprint < ActiveRecord::Migration[4.2]
  def change
    add_column :blueprints, :cpp_blueprint_id, :integer
  end
end

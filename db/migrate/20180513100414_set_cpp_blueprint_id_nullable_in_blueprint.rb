class SetCppBlueprintIdNullableInBlueprint < ActiveRecord::Migration[5.2]
  def change
    change_column :blueprints, :cpp_blueprint_id, :integer, null: true
    remove_index :blueprints, :cpp_blueprint_id
  end
end

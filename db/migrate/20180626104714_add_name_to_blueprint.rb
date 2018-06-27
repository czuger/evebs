class AddNameToBlueprint < ActiveRecord::Migration[5.2]
  def change
    add_column :blueprints, :name, :string
    change_column :blueprints, :nb_runs, :integer, null: false
    change_column :blueprints, :prod_qtt, :integer, null: false
    remove_foreign_key :blueprints, :eve_items
    add_index :blueprints, :cpp_blueprint_id, unique: true
    rename_column :blueprints, :eve_item_id, :produced_cpp_type_id
  end
end

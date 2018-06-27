class AddForeignKeysAndNotNullToAllBlueprintInvolvedTables < ActiveRecord::Migration[5.2]
  def up
    change_column :blueprints, :produced_cpp_type_id, :integer, null: false
    change_column :blueprints, :nb_runs, :integer, null: false
    change_column :blueprints, :prod_qtt, :integer, null: false
    change_column :blueprints, :cpp_blueprint_id, :integer, null: false
    change_column :blueprints, :name, :string, null: false

    change_column :eve_items, :name_lowcase, :string, null: false
    remove_column :eve_items, :epic_blueprint
    remove_column :eve_items, :involved_in_blueprint

    change_column :components, :cpp_eve_item_id, :integer, null: false
    change_column :components, :name, :string, null: false

  end

  def down
    change_column :blueprints, :produced_cpp_type_id, :integer, null: true
    change_column :blueprints, :nb_runs, :integer, null: true
    change_column :blueprints, :prod_qtt, :integer, null: true
    change_column :blueprints, :cpp_blueprint_id, :integer, null: true
    change_column :blueprints, :name, :string, null: true

    change_column :eve_items, :name_lowcase, :string, null: true
    add_column :eve_items, :epic_blueprint, :boolean
    add_column :eve_items, :involved_in_blueprint, :boolean

    change_column :components, :cpp_eve_item_id, :integer, null: true
    change_column :components, :name, :string, null: true
  end
end

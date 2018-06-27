class BlueprintProducedCppTypeIdIndexUnique < ActiveRecord::Migration[5.2]
  def change
    remove_index :blueprints, :produced_cpp_type_id
    add_index :blueprints, :produced_cpp_type_id, unique: true

    change_column :blueprints, :updated_at, :timestamp, null: false
    change_column :blueprints, :created_at, :timestamp, null: false

    change_column :eve_items, :updated_at, :timestamp, null: false
    change_column :eve_items, :created_at, :timestamp, null: false

    change_column :components, :updated_at, :timestamp, null: false
    change_column :components, :created_at, :timestamp, null: false

    change_column :materials, :updated_at, :timestamp, null: false
    change_column :materials, :created_at, :timestamp, null: false
  end
end

class CreateRegions < ActiveRecord::Migration[4.2]
  def change
    create_table :regions do |t|
      t.string :cpp_region_id, null: false
      t.string :name, null: false

      t.timestamps null: false
    end
    add_index :regions, :cpp_region_id, unique: true
  end
end

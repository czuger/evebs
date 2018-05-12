class CreateTypeInRegions < ActiveRecord::Migration[5.2]
  def change
    create_table :type_in_regions do |t|
      t.integer :cpp_region_id, null: false
      t.integer :cpp_type_id, null: false

      t.timestamps
    end
  end
end

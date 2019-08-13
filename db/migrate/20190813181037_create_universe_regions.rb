class CreateUniverseRegions < ActiveRecord::Migration[5.2]
  def change
    create_table :universe_regions do |t|
      t.integer :cpp_region_id, null: false
      t.string :name, null: false

      t.timestamps
    end
  end
end

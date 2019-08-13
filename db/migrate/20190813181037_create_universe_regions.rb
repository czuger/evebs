class CreateUniverseRegions < ActiveRecord::Migration[5.2]
  def change
    create_table :universe_regions do |t|
      t.integer :cpp_region_id, null: false, index: { unique: true }
      t.string :name, null: false

      t.timestamps
    end
  end
end

class CreateUniverseConstellations < ActiveRecord::Migration[5.2]
  def change
    create_table :universe_constellations do |t|
      t.integer :cpp_constellation_id, null: false, index: { unique: true }
      t.string :name, null: false
      t.references :universe_regions, null: false, foreign_key: true, index: true

      t.timestamps
    end
  end
end

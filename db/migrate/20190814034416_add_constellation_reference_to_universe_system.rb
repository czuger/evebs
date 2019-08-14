class AddConstellationReferenceToUniverseSystem < ActiveRecord::Migration[5.2]
  def change
    remove_column :universe_systems, :cpp_constellation_id, :integer
    add_reference :universe_systems, :universe_constellation, foreign_key: true, index: true

    remove_column :universe_systems, :stations_ids, :integer, null: false, array: true, default: []
    remove_column :universe_stations, :cpp_system_id, :integer
  end
end

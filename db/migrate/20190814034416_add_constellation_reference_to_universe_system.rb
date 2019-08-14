class AddConstellationReferenceToUniverseSystem < ActiveRecord::Migration[5.2]
  def change
    remove_column :universe_systems, :cpp_constellation_id, :integer
    add_reference :universe_systems, :universe_constellation, foreign_key: true, index: true
  end
end

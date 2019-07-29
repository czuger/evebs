class AddReferenceOnUniverseSystemToUniverseStation < ActiveRecord::Migration[5.2]
  def change
    add_reference :universe_stations, :universe_systems, foreign_key: true, index: :true
  end
end

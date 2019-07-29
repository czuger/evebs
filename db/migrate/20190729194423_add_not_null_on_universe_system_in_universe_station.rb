class AddNotNullOnUniverseSystemInUniverseStation < ActiveRecord::Migration[5.2]
  def change
    change_column :universe_stations, :universe_systems_id, :bigint, null: false
  end
end

class CreateStations < ActiveRecord::Migration
  def change
    create_table :stations do |t|
      t.references :trade_hub, index: true
      t.string :name
      t.integer :cpp_station_id

      t.timestamps
    end
    add_index :stations, :cpp_station_id
  end
end

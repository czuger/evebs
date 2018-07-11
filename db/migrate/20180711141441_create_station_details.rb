class CreateStationDetails < ActiveRecord::Migration[5.2]
  def change
    create_table :station_details do |t|

      t.integer :cpp_system_id, null: false
      t.integer :cpp_station_id, null: false, index: { unique: true }

      t.string :name, null: false
      t.string :services, null: false, array: true
      t.float :office_rental_cost, null: false

      t.timestamps

      t.references :station, foreign_key: true
    end
  end
end

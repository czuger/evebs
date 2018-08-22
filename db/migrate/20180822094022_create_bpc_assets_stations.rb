class CreateBpcAssetsStations < ActiveRecord::Migration[5.2]
  def change
    create_table :bpc_assets_stations do |t|
      t.references :user, foreign_key: true, null: false
      t.references :station_detail, foreign_key: true, null: false

      t.boolean :touched, null: false, default: false

      t.timestamps
    end
  end
end

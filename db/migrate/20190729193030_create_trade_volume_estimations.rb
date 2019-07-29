class CreateTradeVolumeEstimations < ActiveRecord::Migration[5.2]
  def change
    create_table :trade_volume_estimations do |t|
      t.references :universe_station, foreign_key: true, index: false
      t.references :eve_item, foreign_key: true, index: false
      t.string :day_timestamp, null: false
      t.bigint :volume_total_sum, null: false, default: 0
      t.float :volume_percent, null: false, default: 0

      t.timestamps
    end

    add_index :trade_volume_estimations, [ :universe_station_id, :eve_item_id ], unique: true, name: 'index_trade_volume_estimations_on_us_id_and_eve_item_id'
  end
end

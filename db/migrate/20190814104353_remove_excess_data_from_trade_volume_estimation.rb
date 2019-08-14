class RemoveExcessDataFromTradeVolumeEstimation < ActiveRecord::Migration[5.2]
  def change
    remove_column :trade_volume_estimations, :day_timestamp, :varchar
    remove_column :trade_volume_estimations, :orders, :bigint
    remove_column :trade_volume_estimations, :volume_percent, :float

    remove_column :trade_volume_estimations, :universe_station_id, :bigint

    add_reference :trade_volume_estimations, :universe_system, null: false, foreign_key: true, index: true
    add_reference :trade_volume_estimations, :universe_region, null: false, foreign_key: true, index: true
  end
end

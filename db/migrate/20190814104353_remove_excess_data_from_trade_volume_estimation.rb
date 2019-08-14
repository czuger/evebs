class RemoveExcessDataFromTradeVolumeEstimation < ActiveRecord::Migration[5.2]
  def change
    remove_column :trade_volume_estimations, :day_timestamp, :varchar
    remove_column :trade_volume_estimations, :orders, :bigint
    remove_column :trade_volume_estimations, :volume_percent, :float

    remove_column :trade_volume_estimations, :universe_station_id, :bigint

    add_reference :trade_volume_estimations, :universe_system, null: false, foreign_key: true

    add_index :trade_volume_estimations, [:universe_system_id, :eve_item_id], unique: true, name: :trade_volume_estimations_fk_idx

    rename_column :trade_volume_estimations, :volume_total_sum, :volume_total
    change_column :trade_volume_estimations, :eve_item_id, :bigint, null: false

    add_column :trade_volume_estimations, :region_volume_total, :bigint, null: false
    add_column :trade_volume_estimations, :percentage, :float, null: false
  end
end

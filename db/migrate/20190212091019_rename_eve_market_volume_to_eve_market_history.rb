class RenameEveMarketVolumeToEveMarketHistory < ActiveRecord::Migration[5.2]
  def change
    rename_table :eve_market_volumes, :eve_market_histories
    add_column :eve_market_histories, :highest, :float
    add_column :eve_market_histories, :lowest, :float
    add_column :eve_market_histories, :average, :float
    add_column :eve_market_histories, :order_count, :bigint
    add_column :eve_market_histories, :server_date, :date
  end
end

class AddWatchMyPricesToUser < ActiveRecord::Migration
  def change
    add_column :users, :watch_my_prices, :boolean
  end
end

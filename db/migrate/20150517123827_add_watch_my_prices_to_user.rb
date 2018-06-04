class AddWatchMyPricesToUser < ActiveRecord::Migration[4.2]
  def change
    add_column :users, :watch_my_prices, :boolean
  end
end

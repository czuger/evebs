class CreateGroupEveMarketHistories < ActiveRecord::Migration[5.2]
  def change
    create_view :group_eve_market_histories
  end
end

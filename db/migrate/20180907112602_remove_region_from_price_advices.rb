class RemoveRegionFromPriceAdvices < ActiveRecord::Migration[5.2]
  def change
    remove_column :prices_advices, :region_id
    rename_column :prices_advices, :avg_price, :avg_price_month
    rename_column :prices_advices, :price_avg_week, :avg_price_week
    rename_column :prices_advices, :daily_monthly_pcent, :immediate_montly_pcent
    drop_table :jita_margins
  end
end

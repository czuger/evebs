class UpdateBuyOrdersAnalyticsResultsToVersion3 < ActiveRecord::Migration[5.2]
  def change
    update_view :buy_orders_analytics_results, version: 3, revert_to_version: 2
  end
end

class UpdateBuyOrdersAnalyticsResultsToVersion2 < ActiveRecord::Migration[5.2]
  def change
    update_view :buy_orders_analytics_results, version: 2, revert_to_version: 1
  end
end

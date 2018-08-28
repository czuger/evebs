class CreateBuyOrdersAnalyticsResults < ActiveRecord::Migration[5.2]
  def change
    create_view :buy_orders_analytics_results
  end
end

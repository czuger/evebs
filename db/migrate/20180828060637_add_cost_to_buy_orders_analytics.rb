class AddCostToBuyOrdersAnalytics < ActiveRecord::Migration[5.2]
  def change
    add_column :buy_orders_analytics, :single_unit_cost, :float
    add_column :buy_orders_analytics, :single_unit_margin, :float
    add_column :buy_orders_analytics, :estimated_volume_margin, :float
    add_column :buy_orders_analytics, :per_job_margin, :float
    add_column :buy_orders_analytics, :per_job_run_margin, :float
    add_column :buy_orders_analytics, :final_margin, :float
  end
end

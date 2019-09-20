class AddMinDefaultsToUser < ActiveRecord::Migration[5.2]
  def change
		drop_view :price_advice_margin_comps
		drop_view :buy_orders_analytics_results

		execute 'UPDATE users SET min_amount_for_advice=5000000 WHERE min_amount_for_advice IS NULL;'
		execute 'UPDATE users SET min_pcent_for_advice=20 WHERE min_pcent_for_advice IS NULL;'
		execute 'UPDATE users SET vol_month_pcent=5 WHERE vol_month_pcent IS NULL;'

		execute 'UPDATE users SET batch_cap=true WHERE batch_cap IS NULL;'
		execute 'UPDATE users SET batch_cap_multiplier=10 WHERE batch_cap_multiplier IS NULL;'

    change_column :users, :min_amount_for_advice, :integer, null: false, default: 5000000
		change_column :users, :min_pcent_for_advice, :integer, null: false, default: 20
		change_column :users, :vol_month_pcent, :integer, null: false, default: 5

		change_column :users, :batch_cap, :boolean, null: false, default: true
		change_column :users, :batch_cap_multiplier, :integer, null: false, default: 10

		create_view :price_advice_margin_comps, version: 7
		create_view :buy_orders_analytics_results, version: 3
  end
end

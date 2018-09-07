class RemoveOldOrdersTables < ActiveRecord::Migration[5.2]
  def change
    drop_view :price_advice_margin_comps
    drop_table :buy_orders
    drop_table :sales_orders
    drop_table :sales_orders_process_infos
    drop_table :tmp_download_blueprints
    drop_table :type_in_regions
    remove_column :prices_advices, :cost
    remove_column :prices_advices, :single_unit_cost
    remove_column :prices_advices, :min_price
    remove_column :prices_advices, :prod_qtt
    remove_column :prices_advices, :full_batch_size
  end
end

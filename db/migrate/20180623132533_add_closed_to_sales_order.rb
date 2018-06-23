class AddClosedToSalesOrder < ActiveRecord::Migration[5.2]
  def change
    add_column :sales_orders, :closed, :boolean, default: false

    # Don't really improve performances
    # add_index :sales_orders, :retrieve_session_id
  end
end

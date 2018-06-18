class AddRegularReferencesToSalesOrder < ActiveRecord::Migration[5.2]
  def change
    add_reference :sales_orders, :trade_hub, foreign_key: true
    add_reference :sales_orders, :eve_item, foreign_key: true
  end
end

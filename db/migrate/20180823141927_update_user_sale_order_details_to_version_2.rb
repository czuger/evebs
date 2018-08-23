class UpdateUserSaleOrderDetailsToVersion2 < ActiveRecord::Migration[5.2]
  def change
    # Normally update view, but we dropped it to modify linked tables.
    create_view :user_sale_order_details, version: 2
  end
end

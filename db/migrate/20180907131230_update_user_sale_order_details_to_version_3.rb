class UpdateUserSaleOrderDetailsToVersion3 < ActiveRecord::Migration[5.2]
  def change
    create_view :user_sale_order_details, version: 3
  end
end

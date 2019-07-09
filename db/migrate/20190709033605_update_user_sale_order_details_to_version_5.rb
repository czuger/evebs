class UpdateUserSaleOrderDetailsToVersion5 < ActiveRecord::Migration[5.2]
  def change
    update_view :user_sale_order_details, version: 5, revert_to_version: 4
  end
end

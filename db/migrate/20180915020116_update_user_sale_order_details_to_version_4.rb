class UpdateUserSaleOrderDetailsToVersion4 < ActiveRecord::Migration[5.2]
  def change
    update_view :user_sale_order_details, version: 4, revert_to_version: 3
  end
end

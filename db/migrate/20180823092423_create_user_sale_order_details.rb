class CreateUserSaleOrderDetails < ActiveRecord::Migration[5.2]
  def change
    create_view :user_sale_order_details
  end
end

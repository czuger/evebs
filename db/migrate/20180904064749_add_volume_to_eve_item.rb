class AddVolumeToEveItem < ActiveRecord::Migration[5.2]
  def change
    drop_view :user_sale_order_details

    add_column :eve_items, :volume, :bigint
    change_column :eve_items, :blueprint_id, :bigint, null: true
  end
end

class CreateSalesOrdersProcessInfos < ActiveRecord::Migration[5.2]
  def change
    create_table :sales_orders_process_infos do |t|
      t.string :key, null: false
      t.integer :last_retrieve_session_id, null: false

      t.timestamps
    end

    add_column :sales_orders, :retrieve_session_id, :integer, index: true
    ActiveRecord::Sequence.create('sales_orders_retrieve_session_id')

  end
end

class CreateSaleRecords < ActiveRecord::Migration[4.2]
  def change
    create_table :sale_records do |t|

      t.references :user, index: true, null: false
      t.references :eve_client, index: true, null: false
      t.references :eve_item, index: true, null: false
      t.references :station, index: true, null: false

      t.string :eve_transaction_key, null: false
      t.integer :quantity, null: false
      t.float :unit_sale_price, null: false
      t.float :total_sale_price, null: false

      t.float :unit_cost
      t.float :unit_sale_profit
      t.float :total_sale_profit

      t.datetime :transaction_date_time, null: false

      t.timestamps
    end

    add_index :sale_records, :eve_transaction_key, unique: true

    # create_join_table :sale_records, :eve_clients, column_options: {null: true} do |t|
    #   t.index :sale_record_id
    #   t.index :eve_client_id
    # end
    # create_join_table :sale_records, :eve_items, column_options: {null: true} do |t|
    #   t.index :sale_record_id
    #   t.index :eve_item_id
    # end
    # create_join_table :sale_records, :stations, column_options: {null: true} do |t|
    #   t.index :sale_record_id
    #   t.index :station_id
    # end

  end
end

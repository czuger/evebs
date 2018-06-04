class DropTableSaleRecord < ActiveRecord::Migration[4.2]
  def change
    drop_table :sale_records
  end
end

class DropTableSaleRecord < ActiveRecord::Migration
  def change
    drop_table :sale_records
  end
end

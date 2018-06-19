class RenameSalesDailyToSalesFinal < ActiveRecord::Migration[5.2]
  def change
    rename_table :sales_dailies, :sales_finals
  end
end

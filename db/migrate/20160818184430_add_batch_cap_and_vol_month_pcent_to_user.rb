class AddBatchCapAndVolMonthPcentToUser < ActiveRecord::Migration
  def change
    add_column :users, :batch_cap, :boolean, default: false, null: false
    add_column :users, :vol_month_pcent, :integer, default: 20, null: false
  end
end

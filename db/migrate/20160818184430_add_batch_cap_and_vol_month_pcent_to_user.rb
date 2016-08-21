class AddBatchCapAndVolMonthPcentToUser < ActiveRecord::Migration
  def change
    add_column :users, :batch_cap, :boolean, default: true, null: false
    add_column :users, :vol_month_pcent, :integer, default: 10, null: false
  end
end

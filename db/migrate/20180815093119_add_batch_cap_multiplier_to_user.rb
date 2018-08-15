class AddBatchCapMultiplierToUser < ActiveRecord::Migration[5.2]
  def change
    add_column :users, :batch_cap_multiplier, :integer, null: false, default: 1
  end
end

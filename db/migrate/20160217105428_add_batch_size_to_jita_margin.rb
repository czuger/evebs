class AddBatchSizeToJitaMargin < ActiveRecord::Migration[4.2]
  def change
    add_column :jita_margins, :batch_size, :bigint, default: 0, null: false
  end
end

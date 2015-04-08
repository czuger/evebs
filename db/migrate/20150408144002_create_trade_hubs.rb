class CreateTradeHubs < ActiveRecord::Migration
  def change
    create_table :trade_hubs do |t|
      t.integer :eve_system_id
      t.string :name

      t.timestamps
    end
  end
end

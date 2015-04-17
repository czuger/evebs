class CreateTradeHubsUsers < ActiveRecord::Migration
  def change
    create_table :trade_hubs_users do |t|
      t.references :user, index: true
      t.references :trade_hub, index: true
    end
  end
end

class CreateEveItemsUsers < ActiveRecord::Migration
  def change
    create_table :eve_items_users do |t|
      t.references :user, index: true
      t.references :eve_item, index: true
    end
  end
end

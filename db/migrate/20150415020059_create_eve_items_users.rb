class CreateEveItemsUsers < ActiveRecord::Migration[4.2]
  def change
    create_table :eve_items_users do |t|
      t.references :user, index: true
      t.references :eve_item, index: true
    end
  end
end

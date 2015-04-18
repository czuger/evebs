class CreateUsers < ActiveRecord::Migration
  def change
    drop_table :users
    create_table :users do |t|
      t.string :edit
      t.string :name
      t.boolean :remove_occuped_places
      t.string :key_user_id
      t.string :api_key

      t.timestamps
    end
  end
end

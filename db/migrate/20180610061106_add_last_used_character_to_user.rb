class AddLastUsedCharacterToUser < ActiveRecord::Migration[5.2]
  def change
    add_reference :users, :last_used_character
    add_foreign_key :users, :characters, column: :last_used_character_id

    remove_column :users, :key_user_id
    remove_column :users, :api_key

    remove_column :users, :oauth_token
    remove_column :users, :oauth_expires_at
  end
end

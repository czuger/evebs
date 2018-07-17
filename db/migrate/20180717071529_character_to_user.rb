class CharacterToUser < ActiveRecord::Migration[5.2]
  def change
    add_column :users, :expires_on, :datetime

    add_column :users, :token, :string
    add_column :users, :renew_token, :string

    add_column :users, :locked, :boolean, null: false, default: false

    add_column :users, :download_assets_running, :boolean, null: false, default: false
    add_column :users, :last_assets_download, :datetime

    add_column :users, :user_pl_share_id, :bigint
    add_foreign_key :users, :characters, column: :user_pl_share_id

    remove_column :users, :current_character_id, :bigint

    remove_foreign_key :production_list_share_requests, column: :sender_id
    remove_foreign_key :production_list_share_requests, column: :recipient_id

    add_foreign_key :production_list_share_requests, :users, column: :sender_id
    add_foreign_key :production_list_share_requests, :users, column: :recipient_id
  end
end

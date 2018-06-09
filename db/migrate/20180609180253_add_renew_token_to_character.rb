class AddRenewTokenToCharacter < ActiveRecord::Migration[5.2]
  def change
    add_column :characters, :token, :string
    add_column :characters, :renew_token, :string
  end
end

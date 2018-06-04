class AddUserMessageToApiKeyErrors < ActiveRecord::Migration[4.2]
  def change
    add_column :api_key_errors, :user_message, :string
  end
end

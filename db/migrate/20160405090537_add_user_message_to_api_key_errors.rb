class AddUserMessageToApiKeyErrors < ActiveRecord::Migration
  def change
    add_column :api_key_errors, :user_message, :string
  end
end

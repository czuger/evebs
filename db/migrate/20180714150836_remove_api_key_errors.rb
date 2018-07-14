class RemoveApiKeyErrors < ActiveRecord::Migration[5.2]
  def change
    drop_table :api_key_errors
  end
end

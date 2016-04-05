class CreateApiKeyErrors < ActiveRecord::Migration
  def change
    create_table :api_key_errors do |t|
      t.references :user, index: true, foreign_key: true
      t.string :error_message

      t.timestamps null: false
    end
  end
end

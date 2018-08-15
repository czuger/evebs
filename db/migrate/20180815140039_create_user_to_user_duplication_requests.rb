class CreateUserToUserDuplicationRequests < ActiveRecord::Migration[5.2]
  def change
    create_table :user_to_user_duplication_requests do |t|
      t.integer :sender_id, null: false, index: true
      t.integer :receiver_id, null: false, index: true
      t.string :duplication_type, null: false

      t.timestamps
    end

    add_foreign_key :user_to_user_duplication_requests, :users, column: :sender_id
    add_foreign_key :user_to_user_duplication_requests, :users, column: :receiver_id
  end
end

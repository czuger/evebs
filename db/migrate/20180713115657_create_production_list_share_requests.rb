class CreateProductionListShareRequests < ActiveRecord::Migration[5.2]
  def change
    create_table :production_list_share_requests do |t|
      t.bigint :sender_id, null: false
      t.bigint :recipient_id, null: false

      t.timestamps
    end

    add_foreign_key :production_list_share_requests, :characters, column: :sender_id
    add_foreign_key :production_list_share_requests, :characters, column: :recipient_id
    add_index :production_list_share_requests, [:recipient_id, :sender_id], unique: true, name: :plsr_unique_index
  end
end

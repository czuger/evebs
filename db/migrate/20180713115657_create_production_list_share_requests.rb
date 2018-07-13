class CreateProductionListShareRequests < ActiveRecord::Migration[5.2]
  def change
    create_table :production_list_share_requests do |t|
      t.bigint :sender_id, null: false, index: :true
      t.bigint :recipient_id, index: true, null: false

      t.timestamps
    end

    add_foreign_key :production_list_share_requests, :characters, column: :sender_id
    add_foreign_key :production_list_share_requests, :characters, column: :recipient_id
  end
end
